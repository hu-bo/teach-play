from .agent import Agent


class LLMAgent(Agent):
    def __init__(self, model=None):
        self.model = model

    def next_action(self, state):
        # Placeholder that would call an LLM to decide next action
        return {'action': 'noop'}
