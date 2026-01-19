# indexer.py
import boto3
import requests
import json
from requests_aws4auth import AWS4Auth
from langchain_community.embeddings import BedrockEmbeddings
from config import (
    OPENSEARCH_ENDPOINT, 
    REGION, 
    INDEX_NAME, 
    EMBEDDING_MODEL_ID, 
    EMBEDDING_DIMENSION
)

# ----------------------------------------------------
# AWS 클라이언트 및 인증 설정
# ----------------------------------------------------

# boto3 클라이언트 (Bedrock, OpenSearch 인증을 위해 사용)
session = boto3.Session(region_name=REGION)
bedrock_runtime = session.client(service_name='bedrock-runtime', region_name=REGION)
credentials = session.get_credentials()

# OpenSearch 인증 (EC2 IAM Role 사용)
awsauth = AWS4Auth(
    credentials.access_key, 
    credentials.secret_key, 
    REGION, 
    'es', 
    session_token=credentials.token
)

headers = {"Content-Type": "application/json"}

# LangChain Bedrock Embeddings 모델 초기화
embeddings_model = BedrockEmbeddings(
    client=bedrock_runtime,
    model_id=EMBEDDING_MODEL_ID,
    region_name=REGION
)

# ----------------------------------------------------
# OpenSearch 인덱스 스키마 정의 (F-004)
# ----------------------------------------------------

INDEX_BODY = {
    "settings": {
        "index": {
            "knn": True 
        }
    },
    "mappings": {
        "properties": {
            "vector_field": {
                "type": "knn_vector",
                "dimension": EMBEDDING_DIMENSION,
                "method": {
                    "name": "hnsw",
                    "space_type": "l2",
                    "engine": "nmslib"
                }
            },
            "text": {"type": "text"},
            "source": {"type": "keyword"},
            "page_number": {"type": "integer"}
        }
    }
}

# ----------------------------------------------------
# 인덱싱 기능 함수
# ----------------------------------------------------

def create_opensearch_index():
    """
    OpenSearch 인덱스를 생성하거나 이미 존재하면 확인합니다.
    """
    url = f"https://{OPENSEARCH_ENDPOINT}/{INDEX_NAME}"
    try:
        response = requests.put(url, auth=awsauth, headers=headers, data=json.dumps(INDEX_BODY))
        response.raise_for_status()
        print(f"인덱스 '{INDEX_NAME}' 생성 완료.")
    except requests.exceptions.HTTPError as e:
        if response.status_code == 400 and "already exists" in response.text:
            print(f"인덱스 '{INDEX_NAME}' 이미 존재함. 재사용합니다.")
        else:
            print(f"인덱스 생성 실패: HTTP {response.status_code} - {response.text}")
            raise e

def index_documents(docs):
    """
    분할된 문서를 벡터화하여 OpenSearch에 벌크 인덱싱합니다. (F-001)
    """
    create_opensearch_index() # 인덱스 생성 선행

    print(f"{len(docs)}개 청크 임베딩 및 인덱싱 시작...")
    
    bulk_data = []
    
    # LangChain의 get_embeddings() 함수를 사용하면 여러 청크를 한 번에 처리하여 효율적입니다.
    texts = [doc.page_content for doc in docs]
    vectors = embeddings_model.embed_documents(texts) 
    
    for i, (doc, vector) in enumerate(zip(docs, vectors)):
        # 1) 메타데이터 (인덱스 요청)
        bulk_data.append(json.dumps({
            "index": {
                "_index": INDEX_NAME, 
                "_id": f"pdf_chunk_{i}"
            }
        }))
        
        # 2) 문서 데이터
        metadata = doc.metadata
        bulk_data.append(json.dumps({
            "text": doc.page_content,
            "vector_field": vector,
            "source": metadata.get('source', 'Unknown'),
            "page_number": metadata.get('page', -1)
        }))

    bulk_payload = "\n".join(bulk_data) + "\n"
    bulk_url = f"https://{OPENSEARCH_ENDPOINT}/_bulk"

    try:
        bulk_response = requests.post(
            bulk_url, 
            auth=awsauth, 
            headers={"Content-Type": "application/x-ndjson"},
            data=bulk_payload.encode('utf-8')
        )
        bulk_response.raise_for_status()
        
        # 에러 체크
        response_json = bulk_response.json()
        if response_json.get('errors'):
            print("일부 문서 인덱싱 중 오류가 발생했습니다.")
            # 오류 내용 자세히 출력
            # for item in response_json['items']:
            #     if item['index'].get('error'):
            #         print(f"오류: {item['index']['error']}")

        print(f"총 {len(docs)}개 청크 인덱싱 완료")

    except requests.exceptions.RequestException as e:
        print(f"벌크 인덱싱 실패: {e}")
        raise e
    
    refresh_url = f"https://{OPENSEARCH_ENDPOINT}/{INDEX_NAME}/_refresh"
    refresh_response = requests.post(refresh_url, auth=awsauth, headers={"Content-Type": "application/json"})
    refresh_response.raise_for_status()
    print("인덱스 Refresh 완료. 검색 준비됨.")

# 이 파일 단독 실행 시 인덱스 생성만 테스트
if __name__ == '__main__':
    try:
        create_opensearch_index()
    except Exception as e:
        print(f"테스트 실패: {e}")