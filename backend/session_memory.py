from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict

@dataclass
class SessionState:
    session_id: str
    active_document_id: Optional[str] = None
    last_query: Optional[str] = None
    last_answer: Optional[str] = None
    cited_pages: List[int] = field(default_factory=list)
    active_section: Optional[str] = None
    entities: Dict[str, Any] = field(default_factory=dict) # Tracked dates, names, etc.
    history: List[Dict[str, str]] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)

class SessionMemory:
    _instances: Dict[str, SessionState] = {}

    @classmethod
    def get_session(cls, session_id: str) -> SessionState:
        if session_id not in cls._instances:
            cls._instances[session_id] = SessionState(session_id=session_id)
        
        session = cls._instances[session_id]
        session.last_updated = time.time()
        return session

    @classmethod
    def update_session(cls, session_id: str, **kwargs):
        session = cls.get_session(session_id)
        for k, v in kwargs.items():
            if hasattr(session, k):
                setattr(session, k, v)
        session.last_updated = time.time()

    @classmethod
    def cleanup_old_sessions(cls, max_age_seconds: int = 3600):
        now = time.time()
        to_delete = [
            sid for sid, s in cls._instances.items() 
            if now - s.last_updated > max_age_seconds
        ]
        for sid in to_delete:
            del cls._instances[sid]

    @classmethod
    def get_context_for_llm(cls, session_id: str) -> str:
        session = cls.get_session(session_id)
        parts = []
        if session.last_query:
            parts.append(f"PREVIOUS USER QUERY: {session.last_query}")
        if session.last_answer:
            parts.append(f"PREVIOUS ASSISTANT ANSWER: {session.last_answer}")
        if session.active_section:
            parts.append(f"CURRENT FOCUS SECTION: {session.active_section}")
        if session.cited_pages:
            parts.append(f"RECENTLY DISCUSSED PAGES: {', '.join(map(str, session.cited_pages))}")
        
        return "\n".join(parts)
