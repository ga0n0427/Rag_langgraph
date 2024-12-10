from use_query import cohere_rerank_only, generate_answer, generate_feedback, query_rewrite, filter_contexts_num
from config import FAISS_PATH, TOP_K_RESULTS, llm, MyState
from dotenv import load_dotenv
from langchain_upstage import UpstageGroundednessCheck
from vectorstore_manage import load_faiss_index

load_dotenv()

def update_contexts(state: MyState) -> MyState:
    """
    Chunk들을 State에 업데이트 해주기 위해서 rerank랑 연결해주는 함수 
    
    Args:
        state (MyState): 상태 객체

    Returns:
        MyState: Chunk들이 포함된 업데이트된 상태 객체
    """
    vectorstore = load_faiss_index(FAISS_PATH)
    return update_contexts_rerank(
        state=state,
        vectorstore=vectorstore,
        top_n=TOP_K_RESULTS
    )

def update_contexts_rerank(
    state: MyState,
    vectorstore,
    top_n: int = TOP_K_RESULTS
) -> MyState:
    """
    기존 state의 context를 Cohere로 재정렬된 결과로 업데이트하는 함수.
    
    :param state: 업데이트할 MyState 객체.
    :param vectorstore: FAISS 벡터스토어 객체.
    :param top_n: 반환할 문서 개수.
    :return: context가 업데이트된 MyState 객체.
    """
    try:
        # state에서 query 가져오기
        query = state.get("question", "")
        # cohere_rerank_only를 사용하여 문서 재정렬
        reranked_results = cohere_rerank_only(query, vectorstore, top_n=top_n)
        # context 업데이트
        if reranked_results:
            state["context"] = reranked_results

        else:
            print("No reranked results to update context.")
        return state
    except Exception as e:
        print(f"Error updating context: {e}")
        return state

def filter_contexts(state: MyState) -> MyState:
    """
    제한 조건에 맞지 않는 Document를 state['context']에서 제거.

    Args:
        state (MyState): 현재 상태를 담고 있는 객체.

    Returns:
        MyState: 필터링된 상태 객체.
    """
    try:
        # 제한 조건에 맞지 않는 인덱스 식별
        filtered_indexes = filter_contexts_num(state, llm, state['question'])
        # 인덱스에 해당하는 문서 제거
        state['context'] = [
            doc for i, doc in enumerate(state['context']) if i not in filtered_indexes
        ]
        return state
    except Exception as e:
        print(f"Error filtering context: {e}")
        return state


def update_feedback(state: MyState) -> MyState:
    """
    Chunk와 질문을 통해서 대답의 신뢰도를 판단하기 위한 함수와 연결해주기 위한 함수 
    
    Args:
        state (MyState): 상태 객체

    Returns:
        MyState: 신뢰도 점수(float)와 피드백(string)이 업데이트된 상태 객체
    """
    try:
        state = generate_feedback(state, llm)
        return state
    except Exception as e:
        print(f"Error during feedback {e}")
        return {"error": str(e)}
    
def update_query(state: MyState) -> MyState:
    """
    피드백을 통해 질문을 재작성하는 함수와 연결해주는 함수
    
    Args:
        state (MyState): 상태 객체

    Returns:
        MyState: 재작성된 질문이 업데이트 된 함수
    """
    try:
        state = query_rewrite(state, llm)

        return state
    except Exception as e:
        print(f"Error during update query {e}")
        return {"error": str(e)}
    
def check_groundedness(state: MyState) -> MyState:
    """
    Chunk를 통해서 대답의 신뢰도를 판단하기 위한 함수와 연결해주기 위한 함수(Upstage)
    
    Args:
        state (MyState): 상태 객체

    Returns:
        MyState: 신뢰도 점수가 업데이트된 상태 객체
    """
    try:
        # UpstageGroundednessCheck 객체 초기화
        checker = UpstageGroundednessCheck()

        # 평가를 위한 입력 데이터 구성
        input_data = {
            'context': state.get('context', []),  # context가 없으면 빈 리스트
            'answer': state.get('question', "")  # question이 없으면 빈 문자열
        }
        # Groundedness 평가 수행
        result = checker.invoke(input_data)
        state['check_evaluated'] = result
        return state
    except Exception as e:
        print(f"Error during groundedness evaluation: {e}")
        return state
    
def update_answer(state: MyState) -> MyState:
    """
    Chunk와 질문을 통해서 답변을 생성하는 함수와 연결하는 함수
    
    Args:
        state (MyState): 상태 객체

    Returns:
        MyState: 답변(string)이 업데이트된 상태 객체
    """
    try:
        # 새로운 답변 생성 및 체크
        state = generate_answer(state, llm)

        return state
    except Exception as e:
        print(f"Error updating answer: {e}")
        return state
    