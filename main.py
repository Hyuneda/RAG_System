# main.py
from document_processor import load_and_split_pdf
from indexer import index_documents
from searcher import vector_search, hybrid_search, display_results
from config import OPENSEARCH_ENDPOINT, PDF_PATH

def main():
    """
    PDF 인덱싱 및 검색 시스템 구축의 전체 워크플로우를 실행합니다.
    """
    print("==================================================")
    print("PDF 문서 인덱싱 및 검색 시스템 시작")
    print(f"OpenSearch Endpoint: {OPENSEARCH_ENDPOINT}")
    print(f"PDF 경로: {PDF_PATH}")
    print("==================================================")

    # 1. 텍스트 추출 및 청크 분할 (F-002)
    try:
        docs = load_and_split_pdf()
    except FileNotFoundError as e:
        print(f"오류: {e}")
        print("프로그램을 종료합니다. config.PDF_PATH를 확인해주세요.")
        return
    except Exception as e:
        print(f"PDF 로드 및 분할 중 예외 발생: {e}")
        return

    # 2. 임베딩 생성 및 OpenSearch 인덱싱 (F-001, F-003, F-004)
    try:
        index_documents(docs)
    except Exception as e:
        print(f"인덱싱 중 심각한 오류 발생 (권한/엔드포인트 문제 가능성): {e}")
        print("OpenSearch 엔드포인트 URL 및 EC2 IAM Role 권한을 다시 문의해 주세요.")
        return

    # 3. 검색 테스트 (F-005, F-006)
    
    test_query = "에르고 모션 시트 어떻게 설정하는지 설명해 주세요"
    
    # 3-1. 벡터 검색 (시맨틱 검색)
    try:
        v_results = vector_search(test_query, k=3)
        display_results(v_results, "벡터 검색 (시맨틱)")
    except Exception as e:
        print(f"벡터 검색 실패: {e}")

    # 3-2. 하이브리드 검색 (벡터 + 키워드)
    try:
        h_results = hybrid_search(test_query, k=3)
        display_results(h_results, "하이브리드 검색")
    except Exception as e:
        print(f"하이브리드 검색 실패: {e}")


if __name__ == '__main__':
    main()