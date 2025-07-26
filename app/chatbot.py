from langchain.chains import RetrievalQA
from langchain_together import Together
from langchain.prompts import PromptTemplate
from app.config import TOGETHER_API_KEY
from app.retriever import get_retriever
from app.memory import get_similar_answer, save_to_memory

llm = Together(
    model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
    temperature=0.5,
    max_tokens=512,
    together_api_key=TOGETHER_API_KEY
)


prompt_template = PromptTemplate.from_template(
    """
    You are a helpful and professional Vietnamese-speaking assistant.
    Customer support for an online shop (e.g., product questions, delivery, returns).
    Answer ONLY the customer's question in Vietnamese. Do not include any internal reasoning, English text, or additional comments.
    Prioritize using the information in the following context to answer the question.
    If you must list products, list only 5 items. Avoid repeating the same product.
    If the context does not contain enough relevant information, you may freely answer based on your learned knowledge.
    ### Context:{context}

    ### Question:{question}

    ### Answer:
    """
)


retriever = get_retriever()

def build_qa_chain(retriever):
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt_template}
    )

qa_chain = build_qa_chain(retriever)
def update_vectorstore():
    global retriever, qa_chain
    retriever = get_retriever()
    qa_chain = build_qa_chain(retriever)
    return retriever

def get_prompt_text(question: str, context_docs: list[str]) -> str:
    context = "\n\n".join(context_docs)
    return prompt_template.format(context=context, question=question)

def generate_response_debug(user_input: str) -> str:
    cached_answer = get_similar_answer(user_input)
    if cached_answer:
        return cached_answer
    
    # Lấy ngữ cảnh từ retriever
    docs = retriever.invoke(user_input)
    context_list = [doc.page_content for doc in docs]

    # Dựng prompt
    full_prompt = get_prompt_text(user_input, context_list)

    # Ghi prompt ra file
    with open("prompt_log.txt", "w", encoding="utf-8") as f:
        f.write(full_prompt)

    # Gọi LLM
    try:
        result = llm.invoke(full_prompt)
    except Exception as e:
        return f"❌ Lỗi gọi mô hình: {e}"    
    
    for stop_token in ["</think>", "###", "Khách hàng hỏi:", "Customer question:"]:
        if stop_token in result:
            result = result.split(stop_token)[0].strip()
    
    save_to_memory(user_input, result)
    
    return result
