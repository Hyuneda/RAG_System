# searcher.py
import json
import requests
from indexer import embeddings_model, awsauth, headers
from config import OPENSEARCH_ENDPOINT, INDEX_NAME

# ----------------------------------------------------
# 검색 기능 함수
# ----------------------------------------------------

def vector_search(query_text, k=5):
    """
    쿼리 텍스트를 임베딩하여 OpenSearch에서 k-NN 검색을 수행합니다. (F-005)
    """
    print(f"\n벡터 검색 시작: '{query_text}'")
    
    # 1. 쿼리 텍스트 임베딩
    query_vector = embeddings_model.embed_query(query_text)

    # 2. k-NN 검색 쿼리
    knn_query = {
        "size": k,
        "query": {
            "knn": {
                "vector_field": {
                    "vector": query_vector,
                    "k": k
                }
            }
        },
        "_source": ["text", "source", "page_number"] # F-006 관련 정보
    }

    url = f"https://{OPENSEARCH_ENDPOINT}/{INDEX_NAME}/_search"
    response = requests.post(url, auth=awsauth, headers=headers, data=json.dumps(knn_query))
    response.raise_for_status()
    
    return parse_search_results(response.json())


def hybrid_search(query_text, k=5):
    """
    k-NN과 match 쿼리를 결합합니다.
    """
    print(f"\n🔬 하이브리드 검색 시작 (벡터+키워드): '{query_text}'")
    
    # 1. 쿼리 텍스트 임베딩
    query_vector = embeddings_model.embed_query(query_text)
    
    # 2. OpenSearch의 bool 쿼리를 사용한 단순 하이브리드 쿼리
    hybrid_query = {
        "size": k,
        "query": {
            "bool": {
                # 1. 키워드 검색 (match)
                "should": [
                    {
                        "match": {
                            "text": {
                                "query": query_text,
                                "boost": 2 # 키워드 일치 시 가중치 부여
                            }
                        }
                    },
                    # 2. 벡터 검색 (knn) - bool 쿼리 내에서 knn은 OpenSearch 2.1 이상에서 지원
                    {
                        "knn": {
                            "vector_field": {
                                "vector": query_vector,
                                "k": k,
                                "boost": 1 # 벡터 유사성 가중치
                            }
                        }
                    }
                ],
                "minimum_should_match": 1 # 둘 중 하나만 일치해도 결과 반환
            }
        },
        "_source": ["text", "source", "page_number"]
    }
    
    url = f"https://{OPENSEARCH_ENDPOINT}/{INDEX_NAME}/_search"
    response = requests.post(url, auth=awsauth, headers=headers, data=json.dumps(hybrid_query))
    response.raise_for_status() # 400 에러 재확인
    
    return parse_search_results(response.json())

def parse_search_results(search_response):
    """
    검색 결과를 파싱하여 출력 포맷에 맞춥니다. (F-006)
    """
    results = []
    
    for hit in search_response.get('hits', {}).get('hits', []):
        score = hit.get('_score', 0.0)
        source = hit.get('_source', {})
        
        # 하이라이트된 텍스트 스니펫 
        # 실제 하이라이팅은 OpenSearch 쿼리에 highlight 옵션을 추가해야 하지만, 
        # 여기서는 간단히 텍스트의 일부를 스니펫으로 간주합니다.
        snippet = source.get('text', 'N/A')[:150] + "..." 
        
        results.append({
            "score": score,
            "text": source.get('text'),
            "snippet": snippet,
            "source": source.get('source'),
            "page_number": source.get('page_number')
        })
        
    return results

def display_results(results, search_type):
    """
    검색 결과를 사용자 친화적으로 출력합니다.
    """
    print(f"\n--- {search_type} 검색 결과 ({len(results)}건) ---")
    if not results:
        print("검색된 문서가 없습니다.")
        return

    for i, res in enumerate(results):
        print(f"[{i+1}] 관련도 점수: {res['score']:.4f} (F-006)")
        print(f"    출처: {res['source']} | 페이지: {res['page_number']} (F-006)")
        print(f"    스니펫: {res['snippet']}")
        print("-" * 50)
    
# 이 파일은 main.py에서 임포트하여 사용