from pathlib import Path
from app.services.transcription import _stamp

def test_timestamp_format():
    assert _stamp(61.25) == "00:01:01,250"
