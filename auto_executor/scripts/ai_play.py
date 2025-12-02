import yaml
import time
from pathlib import Path
from auto_executor.core.ai.state_encoder import encode_state
from auto_executor.core.playback.executor import Executor
from auto_executor.core.ai.rule_agent import RuleAgent
from auto_executor.core.ai.openai_agent import OpenAIAgent
from auto_executor.core.playback.action_resolver import resolve_action


def load_ai_config(path=None):
    p = Path(path or Path(__file__).parents[1] / 'config' / 'ai.yaml')
    with open(p, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def run_ai_loop(iterations=10, interval=1.0):
    cfg = load_ai_config()
    agent_type = cfg.get('agent', {}).get('type', 'rule')
    if agent_type == 'openai':
        agent = OpenAIAgent(api_key=cfg['agent'].get('openai_api_key'), prompt_template=cfg['agent'].get('prompt_template'))
    else:
        agent = RuleAgent()

    executor = Executor()

    history = []
    for i in range(iterations):
        state = encode_state(stream_frame=None, ui_tree=None, history=history)
        decision = agent.next_action(state)
        if not decision or decision.get('action') == 'noop':
            time.sleep(interval)
            continue
        # simple: if decision has target as coord dict, call executor to perform
        target = decision.get('target')
        if isinstance(target, dict) and 'x' in target:
            action = {'type': decision.get('action', 'click'), 'position': target}
            executor.actions = [action]
            executor.run()
            history.append(decision)
        time.sleep(interval)


def main():
    run_ai_loop()


if __name__ == '__main__':
    main()
