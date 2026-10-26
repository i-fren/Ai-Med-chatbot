
# import os
# from pathlib import Path

# from dotenv import load_dotenv
# from huggingface_hub import InferenceClient

# from langchain_core.prompts import PromptTemplate
# from langchain_classic.chains import RetrievalQA
# from langchain_core.language_models.llms import LLM
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS


# # STEP 1: Load the .env file
# BASE_DIR = Path(__file__).resolve().parent
# load_dotenv(BASE_DIR / ".env", override=True)

# HF_TOKEN = os.getenv("HF_TOKEN")

# if not HF_TOKEN:
#     raise ValueError(
#         "HF_TOKEN not found. Check your .env file."
#     )


# # STEP 2: Configure the model
# MODEL_ID = "openai/gpt-oss-120b:fastest"


# # Adapter: lets RetrievalQA use Hugging Face chat completions
# class HuggingFaceChatLLM(LLM):
#     client: object
#     model_id: str
#     max_tokens: int = 512

#     @property
#     def _llm_type(self) -> str:
#         return "huggingface-chat-completions"

#     def _call(
#         self,
#         prompt: str,
#         stop=None,
#         run_manager=None,
#         **kwargs,
#     ) -> str:
#         response = self.client.chat_completion(
#             model=self.model_id,
#             messages=[
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=self.max_tokens,
#             temperature=0.5,
#         )

#         answer = response.choices[0].message.content

#         if not answer:
#             return "I don't know based on the available context."

#         return answer


# def load_llm():
#     client = InferenceClient(
#         provider="auto",
#         api_key=HF_TOKEN,
#         timeout=90,
#     )

#     return HuggingFaceChatLLM(
#         client=client,
#         model_id=MODEL_ID,
#         max_tokens=512,
#     )


# # STEP 3: Configure FAISS
# DB_FAISS_PATH = str(
#     BASE_DIR / "vectorstore" / "db_faiss"
# )

# custom_prompt_template = """
# Answer the user's question using only the context below.

# If the answer is not in the context, say you don't know.
# Do not invent facts.

# Context:
# {context}

# Question: {question}

# Answer directly.
# """


# # STEP 4: Create the prompt
# def set_custom_prompt(template):
#     return PromptTemplate(
#         template=template,
#         input_variables=["context", "question"],
#     )


# # STEP 5: Load the existing vector database
# embeddings_model = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )

# db = FAISS.load_local(
#     DB_FAISS_PATH,
#     embeddings_model,
#     allow_dangerous_deserialization=True,
# )


# # STEP 6: Create the retrieval chain
# qa_chain = RetrievalQA.from_chain_type(
#     llm=load_llm(),
#     chain_type="stuff",
#     retriever=db.as_retriever(
#         search_kwargs={"k": 3}
#     ),
#     return_source_documents=True,
#     chain_type_kwargs={
#         "prompt": set_custom_prompt(custom_prompt_template)
#     },
# )


# # STEP 7: Ask questions
# if __name__ == "__main__":
#     while True:
#         user_query = input(
#             "\nEnter your query (or type exit): "
#         ).strip()

#         if user_query.lower() in {"exit", "quit"}:
#             print("Chatbot closed.")
#             break

#         if not user_query:
#             print("Please enter a question.")
#             continue

#         try:
#             response = qa_chain.invoke(
#                 {"query": user_query}
#             )

#             print("\nAnswer:\n")
#             print(response["result"])

#             print("\nSource documents:\n")

#             for i, document in enumerate(
#                 response["source_documents"], start=1
#             ):
#                 print(f"\nSource {i}:")
#                 print(document.page_content[:1000])
#                 print("Metadata:", document.metadata)

#         except Exception as e:
#             print(
#                 f"\nError: {type(e).__name__}: {e}"
#             )

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# STEP 1: Load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found. Check your .env file."
    )


# STEP 2: Configure the Groq language model
def load_llm():
    return ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0.1,
        max_tokens=512,
        api_key=GROQ_API_KEY,
    )


# STEP 3: Configure the existing FAISS database
DB_FAISS_PATH = str(
    BASE_DIR / "vectorstore" / "db_faiss"
)

custom_prompt_template = """
Answer the user's question using only the context below.

If the answer is not in the context, say you don't know.
Do not invent facts.

Context:
{context}

Question: {question}

Answer directly.
"""


# STEP 4: Create the custom prompt
def set_custom_prompt(template):
    return PromptTemplate(
        template=template,
        input_variables=["context", "question"],
    )


# STEP 5: Load Hugging Face embeddings
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# STEP 6: Load the existing FAISS vector database
db = FAISS.load_local(
    DB_FAISS_PATH,
    embeddings_model,
    allow_dangerous_deserialization=True,
)


# STEP 7: Create the RAG retrieval chain
qa_chain = RetrievalQA.from_chain_type(
    llm=load_llm(),
    chain_type="stuff",
    retriever=db.as_retriever(
        search_kwargs={"k": 3}
    ),
    return_source_documents=True,
    chain_type_kwargs={
        "prompt": set_custom_prompt(
            custom_prompt_template
        )
    },
)


# STEP 8: Ask questions
if __name__ == "__main__":
    print("Medical RAG Chatbot")
    print("Using Groq + Hugging Face Embeddings + FAISS")
    print("Type 'exit' to close the chatbot.")

    while True:
        user_query = input(
            "\nEnter your query: "
        ).strip()

        if user_query.lower() in {"exit", "quit"}:
            print("Chatbot closed.")
            break

        if not user_query:
            print("Please enter a question.")
            continue

        try:
            response = qa_chain.invoke(
                {"query": user_query}
            )

            print("\nAnswer:\n")
            print(response["result"])

            print("\nSource documents:\n")

            for i, document in enumerate(
                response["source_documents"],
                start=1,
            ):
                print(f"\nSource {i}:")
                print(document.page_content[:1000])
                print("Metadata:", document.metadata)

        except Exception as e:
            print(
                f"\nError: {type(e).__name__}: {e}"
            )
