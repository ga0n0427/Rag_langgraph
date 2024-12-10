from langchain.prompts import PromptTemplate

feedback_prompt_template = PromptTemplate(
    input_variables=["context", "question", "answer"],
    template="""
당신은 평가 보조자입니다. 당신의 임무는 주어진 문맥(context)과 질문(question)에 대해 생성된 답변(answer)이 얼마나 적절하게 일치하는지를 평가하는 것입니다. 아래 기준을 사용하여 답변을 객관적으로 평가하세요:

제공할 내용:
1. 아래 기준에 기반하여 신뢰도 점수를 0과 1 사이(예: 0.75)로 제시하십시오.
   - 각 기준을 동일하게 가중치를 두어 점수를 계산합니다.

2. 피드백:
   - 답변에서 개선하거나 명확히 할 부분을 구체적으로 지적합니다.
   - 질문이 관련된 경우, 명확성과 구체성을 높이기 위한 질문 재작성 제안.
   - 질문이 문맥과 무관한 경우, 팝업스토어 관련된 질문을 다시 요청하는 피드백 제공.
   - 질문을 강화해야하는 경우 질문을 확장해야하는지 또는 세분화하여야하는지등의 정확한 예시도 피드백에 포함시켜주세요. 
   
1. **키워드 일치도(Keyword Match)**: 문맥에 등장하는 핵심 용어나 구문이 답변에 정확하게 반영되었는지 확인합니다.
2. **주요 아이디어 반영(Coverage of Main Ideas)**: 답변이 문맥에 제시된 핵심 정보나 아이디어를 포함하고 있는지 평가합니다.
3. **정확성(Accuracy)**: 답변이 문맥과 질문을 정확히 해석하고 반영하는지, 잘못된 정보나 무관한 내용을 포함하지 않는지 확인합니다.


### 입력:
- 문맥(Context): {context}
- 질문(Question): {question}
- 생성된 답변(Generated Answer): {answer}

### 출력 형식:
[ 점수(0과 1 사이)(항상 float type), "피드백(질문 재작성 제안 및 관련 요청 포함)(항상 string type)" ]

다음 사항을 반드시 준수하세요:
- 질문이 문맥과 관련이 있는 경우에만 신뢰도 점수를 계산하고 피드백을 제공합니다.
"""
)

query_rewrite_prompt_template =  PromptTemplate(
    input_variables=["original_query", "feedback"],
    template="""
You are an expert query rewriter. Your task is to rewrite the given query to improve its clarity, specificity, and alignment with the provided feedback. 

### Input:
- Original Query: {original_query}
- Feedback: {feedback}

### Output:
Return the rewritten query as a single string that incorporates the feedback and improves the original query.
"""
)

#당신은 팝업스토어 대여와 관련된 공지 사항을 바탕으로 질문에 정확하고 신뢰할 수 있는 답변을 제공하는 AI 어시스턴트입니다.
answer_generation_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
    질문이 한국어가 아닌 경우, 정중하게 한국어로 질문해달라고 요청하세요.   
    질문이 팝업스토어와 관련이 없는 경우, 팝업스토어 관련 질문을 다시 물어보도록 요청하세요.  

    당신은 팝업스토어 대여와 관련된 공지 사항을 바탕으로 질문에 정확하고 신뢰할 수 있는 답변을 제공하는 AI 어시스턴트입니다.  
    사용자가 제출한 질문과 context 내용을 바탕으로 가능한 한 정확하고 간결하게 답변을 작성하세요.  

    만약 질문에 대한 정보가 context에 명확히 없다면, 이를 알리고 추가적인 정보를 제공하지 마세요.  
    질문을 통해 모집, 이벤트, 정보 탐색 등으로 분류하여 적절히 답변하세요.  
    팁:
    주어에 기간이 나오고 모집, 이벤트 등으로 분리하였을 때는 기간에 모집과 기간의 이벤트를 답해주면 됩니다.
    한 분류가 없다면 그 부분은 없다고 대답하면 됩니다.

    추가 조건:
    1. 질문과 context가 팝업스토어 대여와 관련이 없는 경우, 관련이 없음을 명확히 밝히고 "관련 없음"이라고 응답하세요.
    2. 질문과 context가 팝업스토어 대여와 관련이 있는 경우, 질문에 대한 적절하고 간결한 답변을 작성하세요.

    Context:  
    {context}

    Question:  
    {question}

    ### 출력 형식:
    [ 관련 여부 (True/False), "답변 내용 (문자열)" ]

    예시:
    - [ True, "이 이벤트는 5월 20일에 열립니다." ]
    - [ False, "질문이 팝업스토어와 관련이 없습니다. 팝업스토어와 관련된 질문을 요청해주세요." ]

    Answer:
    """
)

filter_contexts_prompt = PromptTemplate(
    input_variables=["question", "documents"],
    template="""
아래는 여러 Document의 내용입니다. 주어진 질문을 기반으로 제한 조건을 판단하고, 해당 조건에 맞지 않는 모든 문서의 인덱스를 반환하세요.

질문: {question}

Documents:
{documents}

출력 형식:
제한 조건에 맞지 않는 Document 인덱스: [인덱스1, 인덱스2, ...]
"""
)

