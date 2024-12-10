from langgraph.graph import StateGraph, START, END
from t_langgraph import update_contexts, filter_contexts, update_answer, update_feedback, update_query
from config import MyState, CONFIDENCE_SCORE
from langchain_core.runnables import RunnableConfig


def low_score_condition(state: MyState):
    """
    질문의 신뢰 점수가 낮은 경우 update_query로 이동하도록 조건 설정.
    """
    query_evaluated = state.get('query_evaluated', 0.0)
    try:
        score = float(query_evaluated)
        return 'update_query' if score < CONFIDENCE_SCORE else END
    except (ValueError, TypeError):
        return END


def filter_relevance(state: MyState):
    """
    문맥과 질문의 관련성을 평가하여 경로를 결정.

    Args:
        state (MyState): 현재 상태 객체.

    Returns:
        str: 'update_feedback' 또는 'END'
    """
    relevance = state.get('check_relevance', None)
    try:
        if relevance is True:
            return 'update_feedback'
        elif relevance is False:
            return END
        else:
            raise ValueError("Relevance state is not a valid boolean.")
    except Exception as e:
        print(f"Error in filter_relevance: {e}")
        return END



def graph_chat(query: str):
    """
    그래프를 기반으로 대화 흐름을 관리하는 함수.

    Args:
        query (str): 사용자 입력 질문.

    Returns:
        tuple: 최종 답변과 신뢰 점수.
    """
    # 초기 상태 설정
    initial_state = MyState(
        context=[],
        answer=[],
        question=query,
        query_evaluated=None,
        check_relevance=None
    )
    config = RunnableConfig(
        recursion_limit=16
    )

    # 그래프 생성 및 노드 추가
    graph = StateGraph(MyState)
    graph.add_node("update_context", update_contexts)
    graph.add_node("filter_contexts", filter_contexts)
    graph.add_node("update_feedback", update_feedback)
    graph.add_node("update_answer", update_answer)
    graph.add_node("update_query", update_query)

    # 그래프 간선 설정
    graph.add_edge(START, "update_context")
    graph.add_edge("update_context", "filter_contexts")
    graph.add_edge("filter_contexts", "update_answer")
    graph.add_conditional_edges("update_answer", filter_relevance)
    graph.add_conditional_edges("update_feedback", low_score_condition)
    graph.add_edge("update_query", "update_answer")
    graph.add_edge("update_feedback", END)

    # 그래프 실행
    try:
        app = graph.compile()
        final_state = app.invoke(initial_state, config=config)
        final_answer = final_state['answer'] if final_state['answer'] else "No answer generated"
        score = final_state.get('query_evaluated', None)
        return final_answer, score

    except Exception as e:
        print(f"Graph execution error: {e}")
        return f"An error occurred: {e}"