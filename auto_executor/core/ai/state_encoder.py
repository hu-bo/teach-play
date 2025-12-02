from core.vision.stream_processor import extract_button_candidates


def encode_state(stream_frame=None, ui_tree=None, history=None):
    """Encode current state for AI agents.

    - `stream_frame` may be a PIL Image; we extract button-like candidates and OCR text.
    - `ui_tree` is optional accessibility tree.
    - `history` is list of previous decisions.
    Returns a dict consumed by agents.
    """
    stream_text = None
    candidates = []
    if stream_frame is not None:
        try:
            candidates = extract_button_candidates(stream_frame)
            stream_text = '\n'.join([c.get('text', '') for c in candidates if c.get('text')])
        except Exception:
            candidates = []
            stream_text = None

    return {
        'stream_text': stream_text,
        'candidates': candidates,
        'ui_tree': ui_tree,
        'history': history or []
    }
