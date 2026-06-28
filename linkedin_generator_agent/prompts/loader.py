# load - something - 
#agent -> prompts , task 

import importlib

DEFAULT_VERSION="v1" #modular

#adityas 
ALLOWED_VERSIONS = {"v1"}

def load_agent_prompts(version: str = DEFAULT_VERSION):
    if version not in ALLOWED_VERSIONS:
        raise ValueError(f"Unknown prompt version: {version}")
    module = importlib.import_module(f"prompts.{version}.agents")
    return {
        "research":module.RESEARCH_AGENT,
        "writer":module.WRITER_AGENT,
        "validator":module.VALIDATOR_AGENT
    }
    
def load_task_prompts(version: str = DEFAULT_VERSION):
    if version not in ALLOWED_VERSIONS:
        raise ValueError(f"Unknown prompt version: {version}")
    module = importlib.import_module(f"prompts.{version}.tasks")
    return {
        "research":module.RESEARCH_TASK,
        "writing":module.WRITING_TASK,
        "validation":module.VALIDATION_TASK
    }