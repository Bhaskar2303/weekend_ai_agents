import json
import time

from google.api_core.exceptions import ResourceExhausted


def parse_json_response(response_str):
        result_str = str(response_str)
        if '```json' in result_str:
            result_str = result_str.split('```json')[1].split('```')[0].strip()
        elif '```' in result_str:
            result_str = result_str.split('```')[1].split('```')[0].strip()
            
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            return json.loads(str(result_str))

def run_with_retry(crew, max_retries: int = 3, initial_wait:int = 5):
    for attempt in range(max_retries):
        try:
            return crew.kickoff()
        except (ResourceExhausted, Exception):
            if attempt < max_retries - 1:
                wait_time = initial_wait * (2 ** attempt)
                print(f"Rate limit hit, waiting {wait_time} sec before retrying.....")
                time.sleep(wait_time)
            else:
                print("Max retreies excedded. Please try again later")
                raise