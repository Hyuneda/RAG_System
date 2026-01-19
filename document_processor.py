# document_processor.py
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import PDF_PATH, CHUNK_SIZE, CHUNK_OVERLAP
import os

def load_and_split_pdf():
    """
    PDF 문서를 로드하고 청크 단위로 분할하여 반환합니다.
    (F-002: 텍스트 추출, 페이지 분리, 청크 분할 및 오버랩)
    """
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF 파일이 경로에 없습니다: {PDF_PATH}")
        
    print(f"{PDF_PATH} 로드 중")
    

    loader = PyPDFLoader(PDF_PATH)
    pages = loader.load()


    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )


    docs = text_splitter.split_documents(pages)

    print(f"원본 페이지 수: {len(pages)}")
    print(f"분할된 청크 수: {len(docs)}")
    
    return docs
    
if __name__ == '__main__':
    try:
        chunks = load_and_split_pdf()
        if chunks:
            print("\n--- 첫 번째 청크 미리보기 ---")
            print(f"내용 (일부): {chunks[0].page_content[:200]}...")
            print(f"메타데이터: {chunks[0].metadata}")
    except FileNotFoundError as e:
        print(f"오류: {e}")