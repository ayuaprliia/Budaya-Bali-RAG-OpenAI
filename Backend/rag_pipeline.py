import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI 
from translate_func import translate_to_english, translate_from_english, detect_language

load_dotenv()

# Embedding dan vectorstore
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb = Chroma(persist_directory="load_data/chroma_db", embedding_function=embedding)
retriever = vectordb.as_retriever(search_type="similarity", top_k=4)

# Model
llm = ChatOpenAI(model_name="gpt-4.1-nano", temperature=0)

# Prompt template
template = """
You are a helpful assistant. Please answer the question based ONLY on the provided context.
If the answer is not in the context, don't make up an answer. Be concise and polite.

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

def query_rag_multilang(user_question: str) -> dict:
    """Enhanced RAG function with topic-aware and usage-aware filtering"""

    input_lang = detect_language(user_question)
    print(f"\n🌐 Detected Language: {input_lang}")

    question_en = translate_to_english(user_question, input_lang)
    result_en = qa_chain(question_en)
    full_answer_en = result_en['result'].strip()

    # Check if model used sources
    if "[SOURCES USED]" in full_answer_en:
        use_sources = True
        clean_answer_en = full_answer_en.replace("[SOURCES USED]", "").strip()
    elif "[NO SOURCE USED]" in full_answer_en:
        use_sources = False
        clean_answer_en = full_answer_en.replace("[NO SOURCE USED]", "").strip()
    else:
        use_sources = False
        clean_answer_en = full_answer_en

    answer_final = translate_from_english(clean_answer_en, input_lang)

    # === DEBUG SOURCE DOCUMENTS ===
    print("\n=== DEBUGGING: SOURCE DOCUMENTS ===")
    for i, doc in enumerate(result_en["source_documents"], 1):
        print(f"[{i}] TITLE:", doc.metadata.get("title"))
        print("     URL  :", doc.metadata.get("url"))
        print("     IMAGE:", doc.metadata.get("image"))
        print("     SAMPLE:", doc.page_content[:80].replace("\n", " "), "...\n")

    # === Filter sources used in the answer ===
    sources = []
    answer_lower = clean_answer_en.lower()
    question_keywords = question_en.lower().split()
    url_to_doc = {}

    # Loop awal: ambil versi dokumen terbaik per URL
    for doc in result_en["source_documents"]:
        url = doc.metadata.get("url", "No URL")
        image = doc.metadata.get("image", "")
        if url not in url_to_doc or (not url_to_doc[url].metadata.get("image") and image):
            url_to_doc[url] = doc

    # Loop kedua: hanya ambil dokumen yang dipakai & relevan dengan pertanyaan
    for url, doc in url_to_doc.items():
        snippet = doc.page_content.strip().lower()
        title = doc.metadata.get("title", "").lower()
        image = doc.metadata.get("image", "")

        print("🟡 Evaluating Document:")
        print("  TITLE:", title)
        print("  URL  :", url)
        print("  IMAGE:", image)

        used_in_answer = snippet[:300] in answer_lower or any(word in answer_lower for word in snippet.split()[:10])
        matches_question = any(word in title or word in snippet for word in question_keywords)

        if used_in_answer and matches_question:
            sources.append({
                "title": doc.metadata.get("title", "No title"),
                "url": url,
                "image": image
            })
            print("  ✅ INCLUDED\n")
        else:
            print("  ❌ NOT INCLUDED\n")

    return {
        "input_language": input_lang,
        "question": user_question,
        "question_english": question_en,
        "answer": answer_final,
        "answer_english": clean_answer_en,
        "sources": sources
    }

def run_multilang_rag_pipeline():
    """Interactive CLI"""
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

if __name__ == "__main__":
    run_multilang_rag_pipeline()