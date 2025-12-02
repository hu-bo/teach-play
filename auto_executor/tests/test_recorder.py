def test_import_recorder():
    from core.recorder.recorder import Recorder
    r = Recorder()
    assert hasattr(r, 'record')
