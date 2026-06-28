import os
import json
from dotenv import load_dotenv

from crewai import Agent,Task, Crew, LLM, Process
from tavily import TavilyClient


from utils import parse_json_response, run_with_retry
from guardrails import validate_input, validate_ouput
from prompts.loader import load_agent_prompts, load_task_prompts

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
        
        agent_prompts = load_agent_prompts(prompt_version)
        tasks_prompts = load_task_prompts(prompt_version)
        
        #agent personality ->
        self.research_agent = Agent(**agent_prompts['research'],verbose=True,llm=self.llm)
        self.writer_agent = Agent(**agent_prompts['writer'],verbose=True,llm=self.llm)
        self.validator_agent = Agent(**agent_prompts['validator'],verbose=True,llm=self.llm)
        
        #one netter way to. call Task 
        self.research_prompt = tasks_prompts["research"]
        self.writing_prompt = tasks_prompts["writing"]
        self.validation_prompt = tasks_prompts["validation"]
        
    def _run_crew(self, agent, description, expected_ouput):
        task = Task(description=description, expected_ouput=expected_ouput, agent=agent)
        crew = Crew(agents=[agent], tasks = [task], process=Process.sequential, verbose=False)
        return run_with_retry(crew)
    
    def research_topic(self, topic):
        queries = [
            f"{topic} latest trends and insights",
            f"{topic} industry statistics",
            f"What is new in {topic} in 2026",
            f"{topic} future outlook and predictions",
            f"Key challenges and opportunites in {topic} ",
        ]
        
        research_data = {"topics":topic, "key_facts":[], "trending_angles":[],"sources":[]}
        
        try:
            for query in queries:
                response = self.tavily.search(query=query, search_depth="advanced",max_results=3)
                for result in response.get("results",[]):
                    research_data['sources'].append({
                        "title":result.get("title"),
                        "url":result.get("url"),
                        "content":result.get("content")
                    })
            return research_data
        except Exception as e:
            print(f"Resesrch Error : {e}")
            return None