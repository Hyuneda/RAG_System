# 📑 RAG System: Hyundai Vehicle Manual Chatbot

[cite_start]현대자동차(MX5 HEV) 차량 사용자 매뉴얼 PDF를 기반으로 한 **고성능 RAG(Retrieval-Augmented Generation) 시스템**입니다. [cite: 1, 15] [cite_start]단순한 텍스트 검색을 넘어, LLM 에이전트가 문맥을 파악하여 정보를 나누는 **Agentic Chunking** 기술을 적용하여 답변의 정확도를 극대화했습니다. [cite: 4, 113]

## 🚀 핵심 기술 (Core Tech Stack)
* [cite_start]**LLM 에이전트**: AWS Bedrock (Claude 3.5 Sonnet) [cite: 3, 38, 39]
* [cite_start]**Vector DB**: Amazon OpenSearch [cite: 3, 37]
* [cite_start]**프레임워크**: LangChain [cite: 3, 34, 35]
* [cite_start]**임베딩 모델**: Amazon Titan Embedding [cite: 47, 201]

## 🧠 주요 특징 (Key Features)

### 1. Agentic Chunking (주제 기반 동적 분할)
[cite_start]단순히 글자 수로 나누는 기존 방식(Simple Chunking)과 달리, LLM이 문맥의 의미 변화를 감지하여 논리적 주제 단위로 청크를 구성합니다. [cite: 4, 225]
* [cite_start]**장점**: 문맥적 완결성을 유지하며 정보 유실을 방지하고 검색 매칭을 최적화합니다. [cite: 208, 209, 211]
* [cite_start]**성능**: 테스트 결과, 하이브리드 검색 점수에서 **41.52**라는 최고점을 기록했습니다. [cite: 131, 226]

### 2. Hybrid Search (하이브리드 검색)
[cite_start]벡터 유사도 검색(Semantic)과 키워드 검색(Keyword)을 결합하여 검색 성능을 극대화했습니다. [cite: 6, 46]
* [cite_start]'BVM(후측방 모니터)', 'HUD'와 같은 **특정 약어 및 전문 용어**에 대한 검색 성능이 뛰어납니다. [cite: 6]

### 3. 고도화된 프롬프트 엔지니어링
[cite_start]현대자동차 차량 매뉴얼 전문 상담원 페르소나를 부여하여, 반드시 제공된 매뉴얼 내용만을 근거로 친절하게 답변하도록 설계되었습니다. [cite: 71, 72, 74]
