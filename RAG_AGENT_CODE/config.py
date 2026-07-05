from functools import cached_property
from pydantic_settings import BaseSettings, SettingsConfigDict


## Settings - typed config 
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        case_sensitive = False,
        extra = 'ignore',
    )
    
#google gemini 
gemini_api_key = None
gemini_model = "gemini-2.0-flash"
temperature = 0.3
max_tokens = 1024 # allow use llm any much as want 


#embeddings  - open source embedding 
embedding_model = "BAAI/bge-small-en-v1.5" 

#vectoir stire - FAISS
faiss_index_path = "./faiss_index"
top_k = 4
chunk_size = 500
chunk_overlap = 50

#memory layer - mongo db
memory_dir = "./memory_store"
memory_window = 10

#tavily 
tavily_api_key = None

#langfuse - optional 
langfuse_public_key = None
langfuse_secret_key = None
langfuse_host = "https://cloud.langfuse.com"


#guardrails
use_guardrails_ai = True

@property
def langfuse_enabled(self):
    return bool(self.langfuse_public_key and self.langfuse_secret_key)

@property
def tavily_enabled(self):
    return bool(self.tavily_api_key)


# build the live onbject rest of your app 
class Providers:
    def __init__(self, settings=None):
        self.settings = settings or Settings()
        
    @cached_property
    def llm(self):
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        if not self.settings.gemini_api_key:
            raise RuntimeError("[config][Providers] Gemini api key is missing")
        
        return ChatGoogleGenerativeAI(
            model = self.settings.gemini_model,
            google_api_key = self.settings.gemini_api_key,
            temperature = self.settings.temperature,
            max_output_tokens = self.settings.max_tokens,
        )
    @cached_property
    def embeddings(self):
        from langchain_community.embeddings import FastEmbedEmbeddings
        return FastEmbedEmbeddings(model_name = self.settings.embedding_model)
    
    @cached_property
    def langfuse_handler(self):
        if not self.settings.langfuse_enabled:
            return None
        try:
            from langfuse.callback import CallbackHandler
            
            return CallbackHandler(
                public_key = self.settings.langfuse_public_key,
                secret_key = self.settings.langfuse_secret_key,
                host = self.settings.langfuse_host
            )
        except Exception as exc:
            print(f"[config][Providers] Failed to initialize Langfuse: {exc}")
            return None
        
    def callbacks(self):
        return [self.langfuse_handler] if self.langfuse_handler else []
        
    
