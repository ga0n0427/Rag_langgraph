from .prompts import (
    answer_generation_template, 
    feedback_prompt_template,
    query_rewrite_prompt_template,
    filter_contexts_prompt,
)
import json
from config import MyState , CASH_THRESHOLD
from typing import List

def filter_contexts_num(state: MyState, llm, question: str) -> List[int]:
    """
    주어진 질문을 기반으로 제한 조건을 판단하여 맞지 않는 모든 Document의 인덱스를 반환.

    Args:
        state (MyState): 현재 상태를 담고 있는 객체.
        llm (object): LLM 객체.
        question (str): 질문 내용.

    Returns:
        List[int]: 제한 조건에 맞지 않는 Document들의 인덱스.
    """
    context = state['context']
    
    # Document 내용을 포매팅
    documents_text = "\n".join([f"{i}. {doc.page_content}" for i, doc in enumerate(context)])
    
    # Prompt 생성
    prompt = filter_contexts_prompt.format(
        question=question,
        documents=documents_text
    )
    
    # LLM 호출
    try:
        response = llm.invoke(prompt)  # invoke를 사용하여 LLM 호출
        if not response or not response.content:  # 응답이 없을 경우 처리
            print("No response from LLM.")
            return []

        response_content = response.content.strip()

        # 응답 형식 확인 및 파싱
        if "제한 조건에 맞지 않는 Document 인덱스:" in response_content:
            index_part = response_content.split(":")[1].strip()
            if index_part.startswith("[") and index_part.endswith("]"):
                filtered_indexes = eval(index_part)
                return filtered_indexes
            else:
                print("Response format is invalid.")
        else:
            print("Expected key phrase not found in response.")
        
        return []
    except Exception as e:
        print(f"Error in LLM prompt: {e}")
        return []

def query_rewrite(state: MyState, llm) -> MyState:
    """
    검색 결과와 피드백을 기반으로 쿼리를 재작성합니다.
    
    Args:
        state (MyState): 상태 객체
        llm (ChatOpenAI): LangChain LLM 객체

    Returns:
        MyState: 재작성된 쿼리가 포함된 업데이트된 상태 객체
    """
    try:
        # State에서 데이터 가져오기
        original_query = state.get('question', '')
        query_feedback = state.get('query_feedback', '')
        print(original_query)
        # 템플릿 실행 및 LLM 호출
        query_rewriter = query_rewrite_prompt_template | llm
        rewritten_query_response = query_rewriter.invoke({
            "original_query": original_query,
            "feedback": query_feedback
        })

        # 재작성된 쿼리 추출
        rewritten_query = rewritten_query_response.content.strip()
        # 상태 업데이트
        state['question'] = rewritten_query
        return state
    
    except Exception as e:
        print(f"Error rewriting query: {e}")
        state['rewritten_query'] = None
        return state

    
def generate_answer(state: MyState, llm) -> MyState:
    """
    검색 결과와 재작성된 쿼리를 기반으로 답변을 생성하고, 관련성 여부와 답변을 상태에 업데이트합니다.

    Args:
        state (MyState): 현재 상태 객체.
        llm (ChatOpenAI): LangChain LLM 객체.

    Returns:
        MyState: 관련성 여부와 생성된 답변이 업데이트된 상태 객체.
    """
    try:
        # 상태에서 입력 데이터 가져오기
        context = state.get('context', '')
        question = state.get('question', '')

        # 답변 생성기 호출
        answer_generator = answer_generation_template | llm
        response = answer_generator.invoke({
            "context": context,
            "question": question
        }).content.strip()

        # 응답 파싱
        parsed_response = eval(response)  # 예: [True, "answer"]

        # 결과 검증
        if (
            isinstance(parsed_response, list) and 
            len(parsed_response) == 2 and 
            isinstance(parsed_response[0], bool) and 
            isinstance(parsed_response[1], str)
        ):
            if(parsed_response[0] == False):
                state['query_evaluated'] = CASH_THRESHOLD
            # 상태 업데이트
            state['check_relevance'] = parsed_response[0]  # 관련 여부
            state['answer'] = parsed_response[1]           # 생성된 답변
        else:
            raise ValueError("Invalid response format from LLM.")

        return state
    except Exception as e:
        print(f"Error generating answer: {e}")
        state['check_relevance'] = None
        state['answer'] = f"Error generating answer: {e}"
        return state


def generate_feedback(state: MyState, llm) -> MyState:
    """
    생성된 답변을 컨텍스트와 질문에 대해 평가하고, 피드백으로 상태를 업데이트합니다.

    매개변수(Args):
    state (MyState): 'context', 'question', 'answer'를 포함하는 상태 객체.
    llm (ChatOpenAI): 피드백을 생성하기 위해 사용하는 LangChain LLM 객체.
    feedback_prompt_template (str): 피드백 프롬프트 템플릿.

    반환값(Returns):
    state: 'reliability_score'와 'feedback'이 추가된 업데이트된 상태 객체.
    """
    try:
        # State에서 입력 데이터 가져오기
        context = state.get('context', '')
        question = state.get('question', '')
        answer = state.get('answer', '')

        # 피드백 프롬프트 작성
        feedback_prompt = feedback_prompt_template.format(
            context=context,
            question=question,
            answer=answer
        )

        # LangChain LLM 호출
        feedback_response = llm.invoke(feedback_prompt)  # 문자열로 전달
        
        # LLM의 응답을 파싱하여 신뢰 점수와 피드백 추출
        feedback = eval(feedback_response.content)  # LLM이 반환한 문자열을 리스트로 변환
        # 결과 검증
        if (
            isinstance(feedback, list) and 
            len(feedback) == 2 and 
            isinstance(feedback[0], float) and 
            isinstance(feedback[1], str)
        ):
            # State 업데이트
            state['query_evaluated'] = feedback[0]
            state['query_feedback'] = feedback[1]
            return state
        else:
            raise ValueError("Invalid feedback format received from LLM.")
    except Exception as e:
        print(f"Error generating feedback: {e}")
        state['query_evaluated'] = None
        state['query_feedback'] = f"Error generating feedback: {e}"
        return state
