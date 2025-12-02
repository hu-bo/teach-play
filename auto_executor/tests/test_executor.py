def test_import_executor():
    from core.playback.executor import Executor
    e = Executor()
    assert hasattr(e, 'run')
