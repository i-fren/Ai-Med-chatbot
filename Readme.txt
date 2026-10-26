# 🩺 Medical RAG Chatbot

An AI-powered Medical Chatbot built using **Retrieval-Augmented Generation (RAG)** to answer medical questions based on *The Gale Encyclopedia of Medicine*. The application retrieves relevant information from medical documents and uses a Large Language Model (LLM) to generate context-aware responses through an interactive Streamlit interface.

## 🚀 Features

- **AI-Powered Q&A:** Ask questions about medical topics in natural language.
- **Retrieval-Augmented Generation:** Retrieves relevant information from medical documents before generating answers.
- **Vector Search:** Uses FAISS for efficient similarity-based document retrieval.
- **LLM Integration:** Generates responses using supported language model providers.
- **Interactive UI:** Simple web interface built with Streamlit.
- **Document-Based Responses:** Uses an encyclopedia as the knowledge source.

## 🛠️ Tech Stack

- **Language:** Python
- **Framework:** Streamlit
- **AI Framework:** LangChain
- **Vector Database:** FAISS
- **Embeddings:** Sentence Transformers
- **LLM Providers:** Groq / Hugging Face
- **Environment Management:** Python dotenv

## ⚙️ Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/i-fren/medical-rag-chatbot.git
   cd medical-rag-chatbot
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   Windows:

   ```bash
   .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure your API credentials in a `.env` file according to your selected model provider.

   Example:

   ```env
   GROQ_API_KEY=your_groq_api_key
   HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
   ```

   Use only the credentials required by your code. Never upload your `.env` file or API keys to GitHub.

## ▶️ Run the Application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in your terminal to interact with the chatbot.

## 🧠 How It Works

1. Medical documents provide the knowledge source.
2. Documents are split into smaller text chunks.
3. Embeddings represent the text for similarity search.
4. FAISS retrieves relevant chunks for a user's question.
5. The language model uses the retrieved context to generate an answer.
6. Streamlit displays the response in the web application.

## 🎯 Project Objective

This project demonstrates practical implementation of **Generative AI, Retrieval-Augmented Generation, semantic search, vector databases, and LLM integration** in a domain-specific question-answering application.

## ⚠️ Disclaimer

This chatbot is intended for educational and informational purposes only. It may generate inaccurate or incomplete information and should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional for medical concerns.

## 👩‍💻 Author

**Farheen Mustafa**

GitHub: [@i-fren](https://github.com/i-fren)
