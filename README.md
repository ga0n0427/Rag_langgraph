# **LangGraph-Based Document Search and Q&A System**

This project leverages LangGraph to build a document-based search and Q&A system. It supports efficient document retrieval, LLM-driven response generation, hallucination verification, and real-time database synchronization.

## **Features**

- **PostgreSQL Integration**
  Listens to PostgreSQL notifications and retrieves updated values automatically. Ensures real-time synchronization with the database.

- **Vector Database Support**
  Stores and retrieves embeddings in a vector database (FAISS). Enables fast and accurate similarity-based document retrieval.

- **Document Processing**
  Uses TikToken for token-based input control and semantic chunking to differentiate text meaningfully.
  
- **Cashing**
  For previously high-confidence answers, they are pre-cached to provide quick responses.
  
- **Query Workflow**
![lang_graph](https://github.com/user-attachments/assets/a5faee52-dd99-4c2d-9eb7-46d692b2891d)

 **Start (__start__)**
  The process begins with initializing the workflow.

 **Update Contexts (update_contexts)**
  Relevant contexts are fetched and updated from the PostgreSQL and vector database.

 **Filter Contexts (filter_contexts)**
  The retrieved contexts are filtered to remove irrelevant data, ensuring only the most relevant information proceeds to the next step.

 **Update Answer (update_answer)**
  An answer is generated based on the filtered contexts:

  If the question is irrelevant, the workflow directly ends at the __end__ node.
  If the generated answer has a confidence score below the threshold, the process moves to the update_feedback node.
 **Update Feedback (update_feedback)**
  Feedback is gathered, and the query is rewritten based on the feedback. The workflow then transitions to the update_query node.

 **Update Query (update_query)**
  The rewritten query is used to retrieve new contexts, restarting the flow from the update_contexts node.

 **End (__end__)**
  The workflow concludes successfully when a high-confidence answer is generated or the question is deemed irrelevant.

## **Environment Setup with Conda**

To set up the environment using Conda, follow these steps:

1. Create a new Conda environment:  
   `conda create -n langchain_env python=3.9 -y`

2. Activate the Conda environment:  
   `conda activate langchain_env`

3. Clone the repository:  
   `git clone https://github.com/Y-O-U-R-S/langchain-rag.git`

4. Navigate into the project directory:  
   `cd langchain-rag`

5. Install the required dependencies:  
   `pip install -r requirements.txt`

6. Set up PostgreSQL:  
   Configure your PostgreSQL database to send notifications.

7. Run the application:
     python app.py
   
## **LangGraph 기반 문서 검색 및 Q&A 시스템**
이 프로젝트는 LangGraph를 활용하여 문서 기반 검색 및 Q&A 시스템을 구축합니다. 효율적인 문서 검색, LLM 기반 답변 생성, 할루시네이션 검증, 실시간 데이터베이스 동기화를 지원합니다.

**주요 기능**
- **PostgreSQL 통합**
  PostgreSQL 알림을 수신하여 자동으로 최신 데이터를 가져옵니다. 데이터베이스와 실시간 동기화를 보장합니다.

- **벡터 데이터베이스 지원**
  FAISS를 활용하여 벡터 임베딩을 저장하고 검색합니다. 빠르고 정확한 유사성 기반 문서 검색을 지원합니다.

- **문서 처리**
  TikToken을 사용하여 입력 크기를 제어하고, 의미를 기반으로 텍스트를 구분하는 시맨틱 청킹을 구현합니다.

- **Cohere API 기반 리랭크**
  Cohere API를 활용하여 검색 결과를 재정렬하고, 더욱 관련성 높은 문서를 우선적으로 제공합니다.
  
- **캐싱**
  이전의 신뢰도 높은 대답에 대해서는 미리 캐싱하여 빠르게 대답합니다.
  
- **Query Workflow**

 **Start (__start__)**
  워크플로가 초기화되면서 프로세스가 시작됩니다.

**Update Contexts (update_contexts)**
  PostgreSQL 및 벡터 데이터베이스에서 관련 문맥을 가져와 업데이트합니다.

**Filter Contexts (filter_contexts)**
  검색된 문맥에서 불필요한 데이터를 제거하여, 가장 관련성 높은 정보만 다음 단계로 전달되도록 필터링합니다.

**Update Answer (update_answer)**
  필터링된 문맥을 기반으로 답변을 생성합니다:

  질문이 연관성이 낮은 경우, 워크플로는 end 노드에서 바로 종료됩니다.
  생성된 답변의 신뢰 점수가 기준 이하일 경우, 프로세스는 update_feedback 노드로 이동합니다.
**Update Feedback (update_feedback)**
  피드백을 수집하여 쿼리를 다시 작성합니다. 이후 워크플로는 update_query 노드로 이동합니다.

**Update Query (update_query)**
  다시 작성된 쿼리를 사용하여 새 문맥을 가져오며, 워크플로는 update_contexts 노드에서 다시 시작됩니다.
  
**End (__end__)**
  높은 신뢰도의 답변이 생성되거나 질문이 관련이 없다고 판단될 때 워크플로가 성공적으로 종료됩니다.
