Auto Executor

Minimal MVP for recording and replaying desktop actions.

Structure:
- `core/` : main modules (recorder, playback, ai, vision, utils)
- `scripts/` : CLI scripts (`record.py`, `play.py`)
- `data/` : templates, recordings, logs
- `tests/` : basic tests

See `requirements.txt` for dependencies.

Quick Start (Conda)

- **Create and activate environment**:

```powershell
conda create -n autoexec python=3.10 -y; conda activate autoexec
```

- **Install Python packages** (uses pip inside the Conda env):

```powershell
pip install -r requirements.txt
```

- **Optional: install system deps**:
- On Windows install Tesseract OCR (for `pytesseract`) and add to PATH.

- **Record** (starts recording until you press Ctrl+C):

```powershell
python -m auto_executor.scripts.record
```

- **Play** a recording (replace with your file):

```powershell
python -m auto_executor.scripts.play auto_executor\data\recordings\recording_<ts>.json
```

- **Run tests**:

```powershell
pip install pytest
pytest -q auto_executor\tests
```

Notes
- The recorder uses `pynput` and `Pillow` for input hooks and screenshots.
- `pytesseract` requires Tesseract OCR to be installed separately.
- `pyautogui` will move and click your mouse — use with caution.

AI-Driven Mode (Prompting / Agent)

You can configure a prompting-based agent to make interaction decisions for the entire session.

- **Config**: edit `config/ai.yaml` to choose agent type and set a prompt template.

- Example `config/ai.yaml` keys:
	- `agent.type`: `openai` or `rule`
	- `agent.openai_api_key`: optional (can use `OPENAI_API_KEY` env var)
	- `agent.prompt_template`: instructions the agent receives along with a JSON state

- **Run AI loop** (agent will decide actions and execute them using `pyautogui`):

```powershell
python -m auto_executor.scripts.ai_play
```

- The current `OpenAIAgent` tries to parse a JSON response from the LLM with schema:

```json
{"action": "click|scroll|key|noop", "target": "text_or_coord", "reason": "..."}
```

Notes
- Ensure any LLM API keys are set in `config/ai.yaml` or environment variables before running.
- The AI agent can be extended to use `vision.locator` and `playback.action_resolver` to map textual targets to coordinates.
- Start with `rule` agent (simple heuristics) if you don't have an LLM configured.


