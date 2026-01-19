import os, json, boto3, requests
from requests_aws4auth import AWS4Auth
from langchain_aws import BedrockEmbeddings, ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 환경 설정
OPENSEARCH_ENDPOINT = "vpc-op-an2-hdsteel-poc-ojqio73homvkzwmg4oartqed6u.ap-northeast-2.es.amazonaws.com"
REGION = 'ap-northeast-2'
CHAT_INDEX = "pdf_indexing_agentchunking" 
EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"

# AWS 세션 및 인증
session = boto3.Session(region_name=REGION)
credentials = session.get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, REGION, 'es', session_token=credentials.token)
headers = {"Content-Type": "application/json"}

# 모델 설정
embeddings_model = BedrockEmbeddings(model_id=EMBEDDING_MODEL_ID, region_name=REGION)
chat_llm = ChatBedrock(
    model_id="anthropic.claude-3-5-sonnet-20240229-v1:0", # 또는 3.5 sonnet
    model_kwargs={"temperature": 0.1},
    region_name=REGION
)

def ask_manual_chatbot(question):
    query_vector = embeddings_model.embed_query(question)
    search_query = {
        "size": 3,
        "query": {
            "bool": {
                "should": [
                    {"match": {"text": {"query": question, "boost": 10}}},
                    {"knn": {"vector_field": {"vector": query_vector, "k": 3, "boost": 2}}}
                ]
            }
        }
    }
    
    url = f"https://{OPENSEARCH_ENDPOINT}/{CHAT_INDEX}/_search"
    res = requests.post(url, auth=awsauth, headers=headers, data=json.dumps(search_query)).json()
    
    context_list = [hit['_source']['text'] for hit in res.get('hits', {}).get('hits', [])]
    source_info = [f"{hit['_source']['page_number']}페이지" for hit in res.get('hits', {}).get('hits', [])]
    context = "\n\n".join(context_list)
    
    prompt = ChatPromptTemplate.from_template("""
    당신은 현대 차량 매뉴얼을 잘 아는 전문 상담원입니다. 
    아래 제공된 [매뉴얼 내용]을 바탕으로 사용자의 질문에 친절하게 답변하세요.
    [매뉴얼 내용]: {context}
    질문: {question}
    """)

    chain = prompt | chat_llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})
    
    print(f"\n챗봇 답변:\n{answer}")
    print(f"참고 출처: {', '.join(set(source_info))}\n")

if __name__ == "__main__":
    print("현대 차량 매뉴얼 챗봇 (Docker Mode) 시작!")
    while True:
        user_input = input("질문을 입력하세요 (종료: q): ").strip()
        if user_input.lower() in ['q', 'exit', '종료']: break
        if user_input: ask_manual_chatbot(user_input)