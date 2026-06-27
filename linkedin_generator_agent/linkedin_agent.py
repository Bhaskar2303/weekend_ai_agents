import os
import json
from dotenv import load_dotenv

from crewai import Agent,Task, Crew, LLM
from tavily import TavilyClient

load_dotenv() #use this load env 

try:
    from langfuse import Langfuse # official sdk 
    _LANGFUSE_AVAILABLE = True 
except ImportError:
    _LANGFUSE_AVAILABLE = False
    
def _init_langfuse():
    if not _LANGFUSE_AVAILABLE:
        return None
    pub = os.getenv("LANGFUSE_PUBLIC_KEY")
    sec = os.getenv("LANGFUSE_SECRET_KEY")
    if not pub or not sec:
        return None
    return Langfuse(
        public_key=pub,
        secret_key=sec,
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    )
    
class LinkedInPostGenerator:
    VALID_TONES = {"professional","casual","thought-leader"}
    VALID_TYPES = {"story","hot-take","announcement","lesson-learned"}
    
    def __init__(self,prompt_version):
        gemini_key = os.getenv("GEMINI_API_KEY")
        tavily_key = os.getenv("TAVILY_API_KEY")
        
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY not found in enviroment")
        if not tavily_key:
            raise ValueError("TAVILY_API_KEY not found in enviroment")
        
        self.tavily = TavilyClient(api_key=tavily_key)
        self.llm = LLM(model='gemini/gemini-2.5-flash', api_key = gemini_key)
        self.lf = _init_langfuse()