# load chunks and the queru vetoe and pass it to llm 


import os
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document



#load the faiss vector store index once and returmn top k chunks
class Retriever:
    def __init__(self, embeddings, index_path="./faiss_index",top_k=4):
        self.index_path = index_path
        self.top_k = top_k
        self._retriever = self._load(embeddings)
        
    def _load(self, embeddings):
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(
                f"FAISS index notr found at {self.index_path}"
                "Build it first : python ingest.py ./docs"
            )
        store = FAISS.load_local(
            self.index_path,
            allow_dangerous_deserialization=True, #never trust your loccal never load
            embeddings=embeddings,
        )
        return store.as_retriever(search_kwargs={"k": self.top_k})