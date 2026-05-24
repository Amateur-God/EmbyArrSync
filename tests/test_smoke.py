import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_blacklists_json_is_valid():
    data = json.loads((ROOT / "config" / "blacklists.json").read_text(encoding="utf-8"))
    assert isinstance(data.get("BLACKLISTED_TV_SHOWS"), list)
    assert isinstance(data.get("BLACKLISTED_MOVIES"), list)
    assert isinstance(data.get("BLACKLISTED_PATHS"), list)


def test_env_example_exists():
    assert (ROOT / "config" / "EmbyArrSync.env.example").is_file()


def test_requirements_lists_core_deps():
    text = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    for dep in ("requests", "python-dotenv", "python-slugify"):
        assert dep in text
