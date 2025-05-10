from pathlib import Path
import toml

BASE_DIR = Path(__file__).resolve().parent.parent
_raw = toml.load(BASE_DIR / "config" / "config.toml")

output_dir = (BASE_DIR / _raw["paths"]["output_dir_base"]).as_posix()
language = _raw["default"]["language"]
account = _raw["default"]["account"]
source_filepath = _raw["default"]["source_file_path"]
subs_filepath = _raw["default"]["subs_file_path"]
timecodes = _raw["default"]["timecodes"]
clips_json_path = _raw["default"]["clips_json_path"]

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


def set_subs_file_path(filepath):
    global subs_filepath
    subs_filepath = filepath


def set_timecodes(timecodes_array):
    global timecodes
    timecodes = timecodes_array


def set_clips_json_path(path):
    global clips_json_path
    clips_json_path = path


def get_source_file_path():
    return source_filepath


def get_subs_file_path():
    return subs_filepath


def get_language():
    return language


def get_account_config():
    return account_jsons[account]


def get_timecodes():
    return timecodes


def get_clips_json_path():
    return clips_json_path
