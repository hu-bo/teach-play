import os
import json
from .agent import Agent

try:
    import openai
except Exception:
    openai = None


class OpenAIAgent(Agent):
    def __init__(self, api_key=None, prompt_template=None):
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.prompt_template = prompt_template
        if openai and self.api_key:
            openai.api_key = self.api_key

    def next_action(self, state):
        if not openai or not self.api_key:
            return {'action': 'noop', 'reason': 'openai-not-configured'}
        prompt = self.prompt_template or ''
        prompt = prompt + "\n\nState:\n" + json.dumps(state)
        resp = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=150,
        )
        text = resp.choices[0].message.content
        try:
            return json.loads(text)
        except Exception:
            return {'action': 'noop', 'reason': 'invalid-json', 'raw': text}
