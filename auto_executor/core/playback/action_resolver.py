def resolve_action(action, state=None):
    """Resolve an action's target using state (ui_tree, ocr, templates).
    Currently returns the recorded position as fallback.
    """
    if action.get('position'):
        return action['position']
    return None
