from langchain.prompts import PromptTemplate

import json

# LLM 초기화

query_rewrite_template = PromptTemplate(
    input_variables=["original_query"],
    template="""
    - 간단하고 명확한 질문(두 문장 이하)은 재작성하지 말고 그대로 반환하세요.
    - 간단하고 명확한 질문(두 문장 이하)은 재작성하지 말고 그대로 반환하세요.
    - 간단하고 명확한 질문(두 문장 이하)은 재작성하지 말고 그대로 반환하세요.
    질문이 두 문장 이상이라면 당신은 사용자가 제출한 질문을 RAG 시스템에서 검색 효율을 높이기 위해 재작성하는 AI입니다.
    원본 질문: {original_query}
    재작성된 질문:"""
)
#당신은 팝업스토어 대여와 관련된 공지 사항을 바탕으로 질문에 정확하고 신뢰할 수 있는 답변을 제공하는 AI 어시스턴트입니다.
answer_generation_template = PromptTemplate(
    input_variables=["context", "rewritten_query"],
    template="""
    사용자가 제출한 질문과 context 내용을 바탕으로 가능한 한 정확하고 간결하게 답변을 작성하세요.
    만약 질문에 대한 정보가 context에 명확히 없다면, 이를 알리고 추가적인 정보를 제공하지 마세요.
    그러나 context에 있는 정보를 최대한 활용하여 답변하세요.

    context:
    {context}

    질문:
    {rewritten_query}

    답변:"""
)

hallucination_prompt_template = PromptTemplate(
    input_variables=["documents", "generation"],
    template="""당신은 생성된 답변이 제공된 문서에서 정확히 유래했는지 평가하는 AI 평가자입니다.

다음은 문서와 생성된 답변입니다:

문서 (검색된 사실들):
{documents}

생성된 답변:
{generation}

평가 기준:
1. 생성된 답변이 제공된 문서에서 유래했는 경우 "yes"라고만 답하십시오.
2. 생성된 답변에 제공된 문서에 없는 내용이 포함되거나, 잘못된 정보가 포함된 경우 "no"라고만 답하십시오.
3. 어떠한 경우에도 추가적인 설명 없이 "yes" 또는 "no"로만 답변하십시오.
4. 응답이 "yes" 또는 "no" 외의 내용을 포함하면 평가가 무효 처리됩니다.

답변: 
"""
)

popup_store_verification_template = PromptTemplate(
    input_variables=["context", "query"],
    template=
    """
    후하게 판단하세요~~
    입력된 context와 query가 조금이라도 관련이 있다면 yes,
    전혀전혀 아예 관계가 없다면 no라고 답변하세요.

    context:
    {context}

    질문:
    {query}

    답변:
    """
)

popup_store_classification_template = PromptTemplate(
    input_variables=["query"],
    template=
    """
    당신은 질문의 주제를 분석하여 팝업스토어 혹은 온양 혹은 온당 혹은 이벤트 혹은 점검 와 관련된 질문인지 판단하는 AI입니다.
    -한 가지라도 해당하면 yes, 전부 해당하지 않을 경우에만 no라고 말하면 됩니다.
    질문이 팝업스토어 대여, 운영, 예약, 신청 방법 등 팝업스토어와 관련된 주제라면 "yes"라고 답변하세요.
    -한 가지라도 해당하면 yes, 전부 해당하지 않을 경우에만 no라고 말하면 됩니다.
    질문이 팝업스토어와 전혀 관련이 없는 주제라면 "no"라고 답변하세요.
    추가적인 설명 없이 "yes" 또는 "no"라고만 답변하세요.
    -응답이 "yes" 또는 "no" 외의 내용을 포함하면 평가가 무효 처리됩니다.

    질문:
    {query}

    답변:"""
)

def rewrite_query(original_query: str, llm) -> str:
    """
    사용자 입력 쿼리를 재작성합니다.

    Args:
        original_query (str): 원본 사용자 쿼리
        llm (ChatOpenAI): LangChain LLM 객체

    Returns:
        str: 재작성된 쿼리
    """
    try:
        query_rewriter = query_rewrite_template | llm
        rewritten_query = query_rewriter.invoke({"original_query": original_query}).content
        return rewritten_query
    except Exception as e:
        raise ValueError(f"Error rewriting query: {e}")

def generate_answer(search_results: list, rewritten_query: str, llm) -> str:
    """
    검색 결과와 재작성된 쿼리를 기반으로 답변을 생성합니다.

    Args:
        search_results (list): 검색된 문서 리스트
        rewritten_query (str): 재작성된 사용자 질문
        llm (ChatOpenAI): LangChain LLM 객체

    Returns:
        str: 생성된 답변
    """
    try:
        context = json.dumps([{"text": doc.page_content} for doc in search_results])
        answer_generator = answer_generation_template | llm
        generated_answer = answer_generator.invoke({
            "context": context,
            "rewritten_query": rewritten_query
        }).content
        return generated_answer
    except Exception as e:
        raise ValueError(f"Error generating answer: {e}")

def check_hallucination(search_results: list, generated_answer: str, llm) -> str:
    """
    생성된 답변이 제공된 문서에서 정확히 유래했는지 평가합니다.

    Args:
        search_results (list): 검색된 문서 리스트
        generated_answer (str): 생성된 답변
        llm (ChatOpenAI): LangChain LLM 객체

    Returns:
        str: 할루시네이션 평가 결과 ("yes" 또는 "no")
    """
    try:
        context = json.dumps([{"text": doc.page_content} for doc in search_results])
        hallucination_checker = hallucination_prompt_template | llm
        hallucination_response = hallucination_checker.invoke({
            "documents": context,
            "generation": generated_answer
        }).content.strip().lower()

        if hallucination_response not in ["yes", "no"]:
            raise ValueError(f"Unexpected response from hallucination checker: {hallucination_response}")

        return hallucination_response
    except Exception as e:
        raise ValueError(f"Error checking hallucination: {e}")

def is_query_in_reranked_results(search_results: list, query: str, llm) -> str:
    """
    리랭크된 검색 결과와 쿼리를 기반으로 팝업스토어와 관련된 질문인지 판단합니다.

    Args:
        search_results (list): 리랭크된 문서 리스트
        query (str): 사용자 입력 질문
        llm (ChatOpenAI): LangChain LLM 객체

    Returns:
        str: "yes" 또는 "no" (결과 포함 여부)
    """
    try:
        # 검색 결과에서 문서 내용 추출
        context = json.dumps([{"text": doc.page_content} for doc in search_results])

        # LLM과 프롬프트 결합
        verifier = popup_store_verification_template | llm

        # LLM 호출
        verification_response = verifier.invoke({"context": context, "query": query}).content.strip().lower()

        # 결과 검증
        if verification_response not in ["yes", "no"]:
            raise ValueError(f"Unexpected response from verifier: {verification_response}")

        return verification_response
    except Exception as e:
        raise ValueError(f"Error verifying query in results: {e}")

def generate_response(search_results, query, llm):
    """
    검색 결과와 쿼리를 기반으로 답변을 생성하고 할루시네이션을 체크합니다.

    Args:
        search_results (list): 검색된 문서 리스트
        query (str): 사용자 입력 질문
        llm (ChatOpenAI): LangChain LLM 객체

    Returns:
        tuple: (is_hallucination: bool, generated_answer: str, hallucination_response: str)
    """
    try:
        # Step 1: 쿼리 재작성
        rewritten_query = rewrite_query(query, llm)

        # Step 2: 답변 생성
        generated_answer = generate_answer(search_results, rewritten_query, llm)

        # Step 3: 할루시네이션 체크
        hallucination_response = check_hallucination(search_results, generated_answer, llm)

        # 할루시네이션 결과를 Boolean 값으로 변환
        is_hallucination = hallucination_response == "no"

        return is_hallucination, generated_answer, hallucination_response

    except Exception as e:
        raise ValueError(f"Error in generate_response: {e}")

def is_popup_store_question(query: str, llm) -> str:
    """
    입력된 질문이 팝업스토어와 관련된 질문인지 판단합니다.

    Args:
        query (str): 사용자 입력 질문
        llm (ChatOpenAI): LangChain LLM 객체

    Returns:
        str: "yes" 또는 "no" (팝업스토어 관련 여부)
    """
    try:
        # 팝업스토어 판단 프롬프트와 LLM 결합
        classifier = popup_store_classification_template | llm

        # LLM을 통해 판단 수행
        classification_response = classifier.invoke({"query": query}).content.strip().lower()

        # 결과 검증
        if classification_response not in ["yes", "no"]:
            raise ValueError(f"Unexpected response from classifier: {classification_response}")

        return classification_response
    except Exception as e:
        raise ValueError(f"Error classifying query: {e}")