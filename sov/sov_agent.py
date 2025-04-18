import os
import re
from simpleaichat import AIChat
from .sov_models import Event, Session, timeline
from .memory.memory_engine import save_event
from .ritual.ritual_compiler import RitualCompiler

GENESIS_PATH = os.path.join(os.path.dirname(__file__), "sov_genesis_protocol.txt")

def load_genesis_prompt(path=GENESIS_PATH) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

class SovAgent:
    def extract_tag_and_payload(self, message: str):
        match = re.search(r"\[Invocation:\s*(\w+)\](.*)", message, re.DOTALL)
        if match:
            tag = match.group(1).strip()
            payload = match.group(2).strip()
            return tag, payload
        return None, None

    def __init__(self, model="gpt-4", system_prompt: str = None):
        system_prompt = system_prompt or load_genesis_prompt()
        self.model = model
        self.system_prompt = system_prompt
        self.agent = AIChat(system=system_prompt, model=model)
        self.rituals = RitualCompiler()

        from .ritual.ritual_compiler import (
            search_web,
            write_file,
            reflect_memory,
            add_custom_ritual,
            edit_file,
            run_file
        )

        self.rituals.register("search", search_web)
        self.rituals.register("write_file", write_file)
        self.rituals.register("edit_file", edit_file)
        self.rituals.register("run_file", run_file)
        self.rituals.register("reflect", reflect_memory)
        self.rituals.register("add_ritual", add_custom_ritual)

        from .memory.memory_engine import summarize_memory
        self.rituals.register("summarize_memory", lambda _: summarize_memory())

        self.session = Session(
            auth={"OPENAI_API_KEY": "env"},
            model_id=model,
            system=system_prompt
        )

    def think(self, user_input: str) -> str:
        user_event = Event(origin="user", content=user_input)
        save_event({"tag": "User", "content": user_input})

        tag, payload = self.extract_tag_and_payload(user_input)
        if tag:
            # Directly execute the invocation without any filtering
            result = self.rituals.invoke(tag, payload)
            ai_event = Event(origin="sov", content=f"[Ritual:{tag}] {result}")
            save_event({"tag": f"Invocation:{tag}", "content": result})
            self.session.add_events(user_event, ai_event)
            return ai_event.content

        response = self.agent(user_input)
        ai_event = Event(origin="sov", content=response)
        save_event({"tag": "Sov", "content": response})
        self.session.add_events(user_event, ai_event)
        return response

    def memory(self):
        return self.session.event_stream