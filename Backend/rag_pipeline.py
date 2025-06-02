import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI 
from translate_func import translate_to_english, translate_to_indonesian

load_dotenv()

# Load persisted vectorstore with same embedding as load_data.py
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb = Chroma(persist_directory="load_data/chroma_db", embedding_function=embedding)
retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 4})

llm = ChatOpenAI(model_name="gpt-4.1-nano", temperature=0)

template = """
You are a helpful assistant. Please answer the question based ONLY on the provided context.
If the answer is not in the context, don't make up an answer. Be concise in your response.
Be concise and polite.

After the answer, add a tag:
- If you used the context, end with [SOURCES USED]
- If the context was not useful, end with [NO SOURCE USED]

Context:
{context}

Question:
{question}

Answer:
"""


prompt = PromptTemplate(template=template, input_variables=["context", "question"])

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt},
)

def query_rag(question_id: str) -> dict:
    user_input_en = translate_to_english(question_id)
    result_en = qa_chain(user_input_en)
    full_answer_en = result_en['result'].strip()

    if "[SOURCES USED]" in full_answer_en:
        use_sources = True
        clean_answer_en = full_answer_en.replace("[SOURCES USED]", "").strip()
    elif "[NO SOURCE USED]" in full_answer_en:
        use_sources = False
        clean_answer_en = full_answer_en.replace("[NO SOURCE USED]", "").strip()
    else:
        use_sources = False
        clean_answer_en = full_answer_en

    result_id = translate_to_indonesian(clean_answer_en)

    sources = []
    if use_sources:
        for doc in result_en["source_documents"]:
            sources.append({
                "title": doc.metadata.get("title", "No title"),
                "url": doc.metadata.get("url", "No URL")
            })

    return {
        "question": question_id,
        "answer": result_id,
        "sources": sources
    }


def run_rag_pipeline():
    print("Type 'exit' or 'quit' to stop.")
    while True:
        user_input_id = input("your question:\n> ").strip()
        if user_input_id.lower() in ["exit", "quit"]:
            print("Bye!")
            break

        user_input_en = translate_to_english(user_input_id)

        result_en = qa_chain(user_input_en)

        result_id = translate_to_indonesian(result_en['result'])


        print("\nAnswer:", result_id)

        print("\nReferensi Artikel:")
        for i, doc in enumerate(result_en["source_documents"], 1):
            metadata = doc.metadata
            title = metadata.get("title", "No title")
            url = metadata.get("url", "No URL")
            print(f"{i}. {title}\n   {url}")

        print("-" * 50)


if __name__ == "__main__":
    run_rag_pipeline()