from pathlib import Path
import toml

BASE_DIR = Path(__file__).resolve().parent.parent
_raw = toml.load(BASE_DIR / "config" / "config.toml")

output_dir = (BASE_DIR / _raw["paths"]["output_dir_base"]).as_posix()
language = _raw["default"]["language"]
account = _raw["default"]["account"]
source_filepath = _raw["default"]["source_file_path"]

account_jsons = {
    name: {
        "json": (BASE_DIR / acc["json"]).as_posix(),
        "cookies": (BASE_DIR / acc["cookies"]).as_posix(),
        "accountname": acc["accountname"],
    }
    for name, acc in _raw["accounts"].items()
}

def set_language(lang):
    global language
    language = lang

def set_account(acc):
    global account
    account = acc

def set_source_file_path(filepath):
    global source_filepath
    source_filepath = filepath

def get_source_file_path():
    return source_filepath

def get_language():
    return language

def get_account_config():
    return account_jsons[account]
