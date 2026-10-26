from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS 


#STEP 1: Load raw pdf
DATA_PATH = "data/"
def load_pdf_files(data):
    loader = DirectoryLoader(data, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    return documents
documents = load_pdf_files(data = DATA_PATH)
print("LENGTH OF PDF DOCUMENTS: ", len(documents))
#create chuncks
def create_chunks(extracted_data):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,
                                                    chunk_overlap=50)
    txt_chunks = text_splitter.split_documents(extracted_data)
    return txt_chunks
txt_chunks = create_chunks(extracted_data = documents)
print("LENGTH OF CHUNKS: ", len(txt_chunks))
#create vector embeddings
def get_embedding_model():
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embedding_model
embedding_model = get_embedding_model()

#Store embedding in faiss
DB_FAISS_Path = "vectorstore/db_faiss"
db = FAISS.from_documents(txt_chunks, embedding_model)
db.save_local(DB_FAISS_Path)