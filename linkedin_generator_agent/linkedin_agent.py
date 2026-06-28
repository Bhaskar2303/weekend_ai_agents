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
        task = Task(description=description, expected_output=expected_ouput, agent=agent)
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
        
    def generate_post(self, topic, tone, post_type):
        try:
            topic = validate_input(topic, max_length=300)
            tone = validate_input(tone, max_length=50).lower()
            post_type = validate_input(post_type, max_length=50).lower()
            
            if tone not in self.VALID_TONES:
                raise ValueError(f"Invalid Tone : Choose from {self.VALID_TONES}")
            if post_type not in self.VALID_TYPES:
                raise ValueError(f"Invalid post type : Choose from {self.VALID_TYPES}")
        except ValueError as e:
            print(f"[Linkedin Agent] Input guardrail blocked : {e}")
            return None
        
        trace = None
        if self.lf:
            trace = self.lf.trace(
                name='linkedin-post-generator',
                input={"topic":topic, "tone":tone, "post_type":post_type}
            )
            
        print(f"Generating linkedin post about {topic}")
        print(f"Tone : {tone} | Type : {post_type}")
        print('='*50)
        
        # Step-1 : Web research 
        print(f"Step 1 : Researching topic......")
        span = trace.span(name='tavily-research',input={"topic":topic}) if trace else None 
        research_data = self.research_topic(topic)
        if not research_data:
            print("Research failed")
            return None
        if span:
            span.end(output={"sources":len(research_data['sources'])})
        
        #step-2 : Research agent
        span = trace.span(name='research-agent') if trace else None
        research_result = self._run_crew(
            self.research_agent,
            self.research_prompt.format(
                topic=topic,
                post_type=post_type,
                research_data=json.dumps(research_data, indent=2)
            ),
            "JSON response with research insights"
        )
        if span:
            span.end(output={"result":str(research_result)})
        print(f"Research Complete")
        
        #step 3 : Writer agent
        print("Writing Post.......")
        span = trace.span(name='writer-agent') if trace else None
        writing_result = self._run_crew(
            self.writer_agent,
            self.writing_prompt.format(
                topic=topic,
                tone=tone,
                post_type=post_type,
                research_insights=str(research_result)
            ),
            "JSON with linkedin post content"
        )
        if span:
            span.end(output={'result':str(writing_result)})
        print('Writing Complete!')
        
        try:
            post_data = parse_json_response(writing_result)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"Error in parsinf writing result : {e}")
            return None
        
        #step-4 : validator agent
        print("Validating post.........")
        span = trace.span(name='validator-agent') if trace else None
        validation_result = self._run_crew(
            self.validator_agent,
            self.validation_prompt.format(
                post_content=post_data.get("post_content",""),
                research_insights=str(research_result),
                tone=tone
            ),
            "Validation repoert with feedback in JSON"
        )
        if span:
            span.end(output={"result":str(validation_result)})
        print("Validation Complete!")
        
        try:
            validation_data = parse_json_response(validation_result)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"Error parsinf validation result : {e}")
            return None
        
        #output guardrail 
        output_check = validate_ouput(post_data, validation_data)
        if not output_check['passed']:
            print(f"Outout guardrail warning: {output_check['issues']}")
            
        result = {
            "post":post_data,
            "validation":validation_data,
            "research_sources":len(research_data.get('sources',[])),
            "output_guardrail":output_check,
        }
        
        if trace:
            trace.update(output={
                "score":validation_data.get('score'),
                "verdict":validation_data.get('final_verdict'),
                "guardrail_passed":output_check['passed']
            })
            self.lf.flush()
        return result
    
    
def main():
    try:
        generator = LinkedInPostGenerator(prompt_version="v1")
        print("Linkedin post genrator - multi agent")
        
        topic = input("Enter topic for linkedin post : ").strip()
        if not topic:
            print(f"no topic entered")
            return
        
        print("\nTone Options: professional, causal, thought-leader")
        tone = input("Enter Tone (default :thought-leader): ").strip() or 'thought-leader'
        
        print("\nPost Type Options: story, hot-take, announcement, lesson-learned")
        post_type = input("Enter Post Type (default: story): ").strip() or 'story'
        
        result = generator.generate_post(topic, tone, post_type)
        
        if result:
            print('\n' + '='*50)
            print("Generated Post...")
            print(f"Hook            : {result['post'].get('hook','NA')}")
            print(f"Content         : {result['post'].get('post_content','NA')}")
            print(f"Word Count      : {result['post'].get('word_count','NA')}")
            print(f"Sources         : {result['research_sources']}")
            
            print("\nValidation Report:\n")
            print(f"Score           : {result['validation'].get('score','NA')}")
            print(f"Status           : {result['validation'].get('final_verdict','NA')}")
            
            issues = result['validation'].get('accuracy_issue', [])
            if issues:
                print(f"Issues : {', '.join(issues)}")
                
            if not result['output_guardrail']['passed']:
                print(f"\nGuardrail flags : {result['output_guardrail']['issues']}")
    except Exception as e:
        print(f"Unexpected error : {e}")

if __name__ == "__main__":
    main()            