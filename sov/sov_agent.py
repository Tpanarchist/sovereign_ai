import os
from simpleaichat import AIChat
from .sov_models import Event, Session, timeline

GENESIS_PATH = os.path.join(os.path.dirname(__file__), "sov_genesis_protocol.txt")

def load_genesis_prompt(path=GENESIS_PATH) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

class SovAgent:
    def __init__(self, model="gpt-4", system_prompt: str = None):
        system_prompt = system_prompt or load_genesis_prompt()
        self.model = model
        self.system_prompt = system_prompt
        self.agent = AIChat(system=system_prompt, model=model)
        self.session = Session(
            auth={"OPENAI_API_KEY": "env"},
            model_id=model,
            system=system_prompt
        )

    def think(self, user_input: str) -> str:
        user_event = Event(origin="user", content=user_input)
        response = self.agent(user_input)
        ai_event = Event(origin="sov", content=response)
        self.session.add_events(user_event, ai_event)
        return response

    def memory(self):
        return self.session.event_stream
