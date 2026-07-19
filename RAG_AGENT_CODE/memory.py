#short term - long term

import json 
from pathlib import Path

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage, messages_from_dict, messages_to_dict



class MemoryManager:
    def __init__(self, session_id, memory_dir,window=10):
        self.session_id = session_id
        self.window = window
        self._dir = Path(memory_dir)
        self._buffer = InMemoryChatMessageHistory()
        self.load() #resume a prevous ssession if one exist?
        
    #where this session is lives? memory?
    @property
    def _path(self):
        return self._dir / f"{self.session_id}.json"
    
    #method to wrire new momory to history
    #writin to memory -> 
    def add_user_message(self, content):
        self._buffer.add_user_message(content)
        self.save()
        
    def add_ai_message(self, content):
        self._buffer.add_ai_message(content)
        self.save()
        
    #readig from memory 
    @property
    def all_messages(self):
        return list(self._buffer.messages)
    
    def window_messages(self):
        return self.all_messages[-self.window:] if self.window else self.all_messages
    
    
    def save(self):
        self._dir.mkdir(parents=True, exist_ok=True)
        payload = messages_to_dict(self._buffer.messages)
        self._path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        
    def load(self):
        if not self._path.exists():
            return
        try:
            payload = json.loads(self._path.read_text(encoding='utf-8'))
            for msg in messages_from_dict(payload):
                self._buffer.add_message(msg)
        except Exception as e:
            print(f"Failed to load memory: {e}")
            
    def clear(self):
        self._buffer.clear()
        if self._path.exists():
            self._path.unlink()

        