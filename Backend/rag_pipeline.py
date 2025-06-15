import os
import numpy as np
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from sklearn.metrics.pairwise import cosine_similarity

from translate_func import translate_to_english, translate_from_english, detect_language

load_dotenv()

# === Embedding dan Vectorstore ===
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb = Chroma(persist_directory="load_data/chroma_db", embedding_function=embedding)
retriever = vectordb.as_retriever(search_type="similarity", top_k=4)

# === LLM Model ===
llm = ChatOpenAI(model_name="gpt-4.1-nano", temperature=0)

# === Prompt Template ===
template = """
You are a helpful assistant. IT IS IMPORTANT TO ALWAYS answer in the SAME LANGUAGE as the question. 

Use only the information provided in the context to answer the question. Do not make up answers. When possible, include direct facts or quotes from the context.

At the end of the answer, include this tag:
- If you used content from the context: [SOURCES USED]
- If the context was not used at all: [NO SOURCE USED]

Context:
{context}

Question:
{question}

Answer:
"""
prompt = PromptTemplate(template=template, input_variables=["context", "question"])

# === RAG Chain ===
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt},
)

# === Query Function ===
def query_rag_multilang(user_question: str) -> dict:
    input_lang = detect_language(user_question)
    print(f"\n🌐 Detected Language: {input_lang}")

    # Translate to English
    question_en = translate_to_english(user_question, input_lang)

    # Get question embedding
    question_embedding = embedding.embed_query(question_en)
    question_embedding_np = np.array(question_embedding).reshape(1, -1)

    # Run RAG
    result_en = qa_chain(question_en)
    full_answer_en = result_en['result'].strip()

    # Clean tags
    if "[SOURCES USED]" in full_answer_en:
        use_sources = True
        clean_answer_en = full_answer_en.replace("[SOURCES USED]", "").strip()
    elif "[NO SOURCE USED]" in full_answer_en:
        use_sources = False
        clean_answer_en = full_answer_en.replace("[NO SOURCE USED]", "").strip()
    else:
        use_sources = False
        clean_answer_en = full_answer_en

    # Translate answer back to original language
    answer_final = translate_from_english(clean_answer_en, input_lang)

    print("\n=== DEBUGGING: SOURCE DOCUMENTS WITH COSINE SIMILARITY ===")
    sources = []
    rejected_docs = []
    answer_lower = clean_answer_en.lower()
    url_to_doc = {}

    # Filter by best doc per URL
    for doc in result_en["source_documents"]:
        url = doc.metadata.get("url", "No URL")
        image = doc.metadata.get("image", "")
        if url not in url_to_doc or (not url_to_doc[url].metadata.get("image") and image):
            url_to_doc[url] = doc

    for url, doc in url_to_doc.items():
        doc_snippet = doc.page_content.strip().lower()
        doc_title = doc.metadata.get("title", "").lower()
        doc_image = doc.metadata.get("image", "")

        # Calculate cosine similarity
        doc_embedding = embedding.embed_query(doc.page_content)
        doc_embedding_np = np.array(doc_embedding).reshape(1, -1)
        similarity = cosine_similarity(question_embedding_np, doc_embedding_np)[0][0]

        if similarity < 0.5:
            print("🔴 REJECTED DOCUMENT (Below Threshold):")
            print("  TITLE    :", doc_title)
            print("  URL      :", url)
            print("  IMAGE    :", doc_image)
            print(f"  COSINE SIMILARITY: {similarity:.4f}\n")

            # Simpan dokumen yang ditolak jika ingin ditampilkan di frontend
            rejected_docs.append({
                "title": doc.metadata.get("title", "No title"),
                "url": url,
                "image": doc.metadata.get("image", ""),
                "similarity": similarity
            })
            continue

        print("🟡 Evaluating Document:")
        print("  TITLE    :", doc_title)
        print("  URL      :", url)
        print("  IMAGE    :", doc_image)
        print(f"  COSINE SIMILARITY: {similarity:.4f}")

        used_in_answer = any(word in answer_lower for word in doc.page_content.lower().split())
        matches_question = any(word in doc_title or word in doc_snippet for word in question_en.lower().split())

        if use_sources and used_in_answer and matches_question:
            sources.append({
                "title": doc.metadata.get("title", "No title"),
                "url": url,
                "image": doc.metadata.get("image", "")
            })
            print("  ✅ INCLUDED\n")
        else:
            print("  ❌ NOT INCLUDED")
            print(f"     used_in_answer: {used_in_answer}")
            print(f"     matches_question: {matches_question}\n")

    return {
        "input_language": input_lang,
        "question": user_question,
        "question_english": question_en,
        "answer": answer_final,
        "answer_english": clean_answer_en,
        "sources": sources,
        "rejected_documents": rejected_docs  # Optional if you want to display this in frontend
    }


# === CLI Runner ===
def run_multilang_rag_pipeline():
    print("🧠 Budaya Bali RAG Multilingual System")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_input = input("Your question:\n> ").strip()

        if user_input.lower() in ["exit", "quit", "keluar"]:
            print("Goodbye!")
            break

        try:
            result = query_rag_multilang(user_input)

            print(f"\n📌 Answer:\n{result['answer']}")
            if result['sources']:
                print(f"\n📚 Sources Used:")
                for i, source in enumerate(result['sources'], 1):
                    print(f"{i}. {source['title']}")
                    print(f"   {source['url']}")
                    print(f"   📷 Image: {source['image']}")
            else:
                print("\n⚠ No sources included.")

            print("-" * 60)

        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again.")

# === Entry Point ===
if __name__ == "__main__":
    run_multilang_rag_pipeline()
