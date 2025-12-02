from .agent import Agent


class RuleAgent(Agent):
    def __init__(self, rules=None):
        self.rules = rules or []

    def next_action(self, state):
        # trivial rule: if 'next' in OCR text, click it
        stream_text = state.get('stream_text', '') if state else ''
        if '下一步' in stream_text or 'next' in stream_text.lower():
            return {'action': 'click', 'target': '下一步'}
        return {'action': 'noop'}
