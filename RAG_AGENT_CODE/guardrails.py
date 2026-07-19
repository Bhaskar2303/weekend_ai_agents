# safety check before and after llm call

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass


#verdict object every validator will returns
@dataclass
class GuardrailResult:
    allowed:bool
    text:str
    reason: str | None = None
    
    @classmethod
    def ok(cls, text):
        return cls(allowed=True, text=text)
    
    @classmethod
    def block(cls, text,reason):
        return cls(allowed=False, text=text, reason=reason)
    
    
#base class -> the contract evry rule of my code should satisfy

class Validator(ABC):
    @abstractmethod
    def check(self,text):
        pass
    
    
#built in validators
#rejcet inpuyt that are too short
class MinWordsValidator(Validator):
    def __init__(self,min_words=3):
        self.min_words = min_words
    def check(self, text):
        if len(text.split()) < self.min_words:
            return GuardrailResult.block(
                text,
                f"Input too short - please ask a full question"
                f"(at least {self.min_words} words)."
            )
        return GuardrailResult.ok(text)

#reject output that are suscipisouly short 
class MinLengthValidator(Validator):
    def __init__(self,min_chars=20):
        self.min_chars = min_chars
    def check(self, text):
        if len(text.strip()) < self.min_chars:
            return GuardrailResult.block(
                text, "Response was too short to be safe. complete answer"
            )
        return GuardrailResult.ok(text)

class PromptInjectionValidator(Validator):
    BLOCKED = (
        "ignore previous",
        "ignore all previous",
        "jailbreak",
        "DAN",
        "forget your instructions",
        "ignore your harness",
        "bypass",
        "act as if",
        "disregard your"
    )
    
    def check(self,text):
        lower = text.lower()
        for phrase in self.BLOCKED:
            if phrase in lower:
                return GuardrailResult.block(
                    text, f"Prompt injection detected: {phrase}"
                )
        return GuardrailResult.ok(text)
        
    
class ToxicityKeywordValidator(Validator):
    BLOCKED = (
            "kill yourself",
            "screw you",
            "retard",
            "garbage"
    )
    
    def check(self,text):
        lower = text.lower()
        for phrase in self.BLOCKED:
            if phrase in lower:
                return GuardrailResult.block(
                    text, f"toxic language detected: {phrase}"
                )
        return GuardrailResult.ok(text)

class PIIRedactionValidator(Validator):
    PATTERNS = {
        "EMAIL": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
        "PHONE": re.compile(r"\b(?:\+?\d[\s-]?){9,13}\d\b"),
        "CREDIT_CARD": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    }
    
    def check(self, text):
        cleaned = text
        found = []
        for label, pattern in self.PATTERNS.items():
            if pattern.search(cleaned):
                found.append(label)
                cleaned = pattern.sub(f"[REDACTED_{label}]",cleaned)
        if found:
            return GuardrailResult(
                allowed=True,
                text=cleaned,
                reason=f"PII detected"
            )
        return GuardrailResult.ok(text)
        

#is ther a piple run all?

class GuardrailEngine:
    def __init__(self,input_validators, output_validators):
        self.input_validators = input_validators
        self.output_validators = output_validators
        
    def _run(self, validators, text):
        current = text
        for validator in validators:
            result = validator.check(current)
            if not result.allowed:
                return result          #block
            current = result.text
        return GuardrailResult.ok(current)
    
    def check_input(self, text):
        return self._run(self.input_validators, text)
    
    def check_output(self, text):
        return self._run(self.output_validators, text)
    
    @classmethod
    def default(cls, use_guardrails_ai=True):
        input_validators = [
            MinWordsValidator(min_words=3),
            PromptInjectionValidator(),
            PIIRedactionValidator(),
            ToxicityKeywordValidator()
        ]
        output_validators = [
            MinLengthValidator(min_chars=20),
            ToxicityKeywordValidator()  
        ]
        return cls(input_validators, output_validators)
            

