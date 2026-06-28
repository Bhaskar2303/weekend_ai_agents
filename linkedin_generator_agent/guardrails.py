# prompt injections



_BLOCKED_PATTERNS = [
    "ignore previous instructions",
    "disregard your prompt",
    "jailbreak",
    "bypass restrictions",
    "ignore all instructions"
]

MIN_SCORE = 6
MIN_WORDS=50
MAX_WORDS=700


def validate_input(text, max_length):
    if not text or not isinstance(text, str):
        raise ValueError("Input must be a non-empty string data")
    text = text.strip()[:max_length]
    lower = text.lower()
    for pattern in _BLOCKED_PATTERNS:
        if pattern in lower:
            raise ValueError(f"Input rejected : disallowed content detected")
    return text


def validate_ouput(post_data, validation_data):
    issues = []
    
    try:
        score = float(validation_data.get('score',0))
        if score < MIN_SCORE:
            issues.append(f"Quality score {score}/10 below threshold ({MIN_SCORE})")
    except (TypeError, ValueError):
        pass
    
    content = post_data.get('post_content',"")
    word_count = len(content.split())
    if word_count < MIN_WORDS:
        issues.append(f"Post too short : {word_count} words  (min {MIN_WORDS})")
    if word_count > MAX_WORDS:
        issues.append(f"Post too long : {word_count} words (max {MAX_WORDS})")
        
    cringe = validation_data.get("cringe_flags",[])
    if cringe:
        issues.append(f"Cringe phrases detected :{cringe}")
        
    return {"passed":len(issues)==0, "issues":issues}