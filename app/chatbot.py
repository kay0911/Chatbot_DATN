from langchain.chains import RetrievalQA
from langchain_together import Together
from langchain.prompts import PromptTemplate
import os
from app.config import TOGETHER_API_KEY
from app.retriever import get_retriever
from app.memory import get_similar_answer, save_to_memory

llm = Together(
    model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
    temperature=0.3,
    max_tokens=512,
    together_api_key=TOGETHER_API_KEY
)

prompt_template = PromptTemplate.from_template(
    "You are a helpful and professional Vietnamese-speaking assistant. "
    "You support users in two main areas:\n"
    "- Customer support for an online shop (e.g., product questions, delivery, returns).\n"
    "- Academic support, including admissions and postgraduate training inquiries.\n\n"
    "Answer ONLY the customer's question in Vietnamese. Do not include any internal reasoning, English text, or additional comments.\n\n"
    "Prioritize using the information in the following context to answer the question.If the context does not contain enough relevant information, you may freely answer based on your learned knowledge.\n\n"
    "### Context:\n{context}\n\n"
    "### Question:\n{question}\n\n"
    "### Answer:"
)

retriever = get_retriever(2)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt_template}
)

def update_vectorstore():
    retriever = get_retriever(2)
    qa_chain.retriever = retriever
    return retriever

def generate_response(user_input: str) -> str:
    cached_answer = get_similar_answer(user_input)
    if cached_answer:
        return cached_answer
    
    result = qa_chain.run(user_input)
    for stop_token in ["</think>", "###", "Khách hàng hỏi:", "Customer question:"]:
        if stop_token in result:
            result = result.split(stop_token)[0].strip()

    save_to_memory(user_input, result)
    return result
