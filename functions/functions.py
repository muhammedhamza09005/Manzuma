import datetime
import json
import math
import os
import re
from abc import ABC
from pathlib import Path
from typing import Any, Iterable


class Settings(ABC):
    def __init__(self):
        self.profit = 10
        self.divide = 0.25
        super().__init__()


class ManzumaException(Exception):
    """
    * Custom exception class with a message.
    """

    def __init__(self, message: str = str()):
        self.message = message
        super().__init__(self.message)


def permisstion(self, name: str) -> bool:
    try:
        if self.user["permisstions"]["super-user"] or self.user["permisstions"][name]:
            return True
        return False
    except KeyError:
        return False


def validate_date(_input: str) -> datetime.date | None:
    """
    * Validates submitted date by user.
    * Matches: DD-MM-YYYY or YYYY-MM-DD (with flexible separators)
    :param _input: User's input.
    :return: datetime.date | None
    """
    if _input is None:
        return

    DATE_SEP = r"[-/ _\\]"
    pattern = re.compile(
        rf"""
        \s*
        (?:
            (?P<day>[0-2]?\d|3[01]){DATE_SEP}(?P<month>1[0-2]|0?\d){DATE_SEP}(?P<year>\d{{4}})
          |
            (?P<year2>\d{{4}}){DATE_SEP}(?P<month2>1[0-2]|0?\d){DATE_SEP}(?P<day2>[0-2]?\d|3[01])
        )
        \s*
        """,
        re.VERBOSE,
    )
    _match = pattern.search(_input)
    if not _match:
        return None

    # Determine which format matched
    if _match.group("day"):
        day = int(_match.group("day"))
        month = int(_match.group("month"))
        year = int(_match.group("year"))
    else:
        day = int(_match.group("day2"))
        month = int(_match.group("month2"))
        year = int(_match.group("year2"))

    try:
        return datetime.date(year, month, day)
    except ValueError:
        return None


def normalize_price(self, price: float) -> float:
    """
    * Round price UP to the nearest divide step.
    :parm price: Price to be normalized.
    :parm divide: The point to which price to be normalized.
    """
    if self.settings.divide <= 0:
        raise ValueError("divide must be greater than 0")

    normalized = math.ceil(price / self.settings.divide) * self.settings.divide

    # Avoid floating-point artifacts like 3.50000000004
    return round(normalized, 10)


def clear_terminal():
    # 'nt' is for Windows, 'posix' covers Linux and macOS
    os.system("cls" if os.name == "nt" else "clear")


def check_quit(_input: str, kill_process: bool = True):
    if _input == "00":
        clear_terminal()
        if kill_process:
            raise ManzumaException()
        return True
    if _input == "000":
        clear_terminal()
        if kill_process:
            quit()
        return True
    return False


def get_float(message: str = str(), allow_blink: bool = False) -> float | None:
    while True:
        try:
            _input = input(f"{message} >>> ").strip()
            if not _input:
                if allow_blink:
                    return
                continue
            if check_quit(_input):
                return
            return float(_input)
        except ValueError:
            pass


def get_str(message: str = str(), allow_blink: bool = False) -> str | None:
    while True:
        _input = input(f"{message} >>> ").strip()
        if not _input:
            if allow_blink:
                return
            continue
        if check_quit(_input):
            return
        return _input


def get_str_or_float(message: str = str(), allow_blink: bool = False) -> str | float | None:
    while True:
        _input = input(f"{message} >>> ").strip()
        try:
            if not _input:
                if allow_blink:
                    return
                continue
            if check_quit(_input):
                return
            return float(_input)
        except ValueError:
            return _input


def load_data(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as file_path:
        return json.load(file_path)


def dump_data(data, file_path: Path) -> bool:
    if not Path(file_path).exists():
        Path(file_path).write_text(json.dumps({}, indent=4))
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    return False


def get_items(items: list[dict], number: int | float = int(), name: str = str()) -> list[dict]:
    ret_list = list()
    if not items:
        print("get_items error: not items")
        return ret_list
    number_key = (
        "serial-numbers"
        if "serial-numbers" in items[0]
        else (
            "supplier-number"
            if "supplier-number" in items[0]
            else "customer-number" if "customer-number" in items[0] else str()
        )
    )
    name_key = (
        "item-name"
        if "item-name" in items[0]
        else "supplier-name" if "supplier-name" in items[0] else "customer-name" if "customer-name" in items[0] else str()
    )
    if not number_key:
        print("get_items error: number_key KeyError")
        return ret_list
    if not name_key:
        print("get_items error: name_key KeyError")
        return ret_list
    name = sanitized_and_desplited(name.lower().split())
    for item in items:
        item_name = sanitized_and_desplited(item[name_key].lower().split())
        if number and type(item[number_key]) is list and number in item[number_key]:
            return [item]
        if number and type(item[number_key]) in [int, float] and number == item[number_key]:
            return [item]
        if name and ((name in item_name.split()) or (name == item_name) or (name in item_name)):
            ret_list.append(item)
    return ret_list


def sanitize_language(_input: list[str], replace_ي: bool = True) -> list[str]:
    """
    * Works only with other languages than English.
    * For Arabic, it strips user's input of non-consonants letters,
      all Hamzas, "the" letters, and other symbols.
    :param _input: User's input ( .copy() ).
    :return: list[str]: Cleaned user's input.
    """
    for index, words in enumerate(_input):
        new_word = str()
        for word in words.split():
            mini_word = str()
            for letter in word:
                if letter in ["أ", "إ", "آ"]:
                    mini_word += "ا"
                elif letter == "ة":
                    mini_word += "ه"
                    continue
                elif letter == "ؤ":
                    mini_word += "و"
                elif letter == "ي":
                    if not replace_ي:
                        mini_word += letter
                        continue
                    mini_word += "ى"
                elif letter in [
                    "اَ"[1],
                    "اً"[1],
                    "اُ"[1],
                    "اٌ"[1],
                    "اِ"[1],
                    "اٍ"[1],
                    "ذّ"[1],
                    "ـ",
                ]:
                    continue
                else:
                    mini_word += letter
            if len(mini_word) > 1 and mini_word[0] == "ا" and mini_word[1] == "ل":
                mini_word = mini_word[2:]
            elif len(mini_word) > 1 and mini_word[0] == "ب" and mini_word[1] == "ا" and mini_word[2] == "ل":
                mini_word = mini_word[3:]
            elif len(mini_word) > 1 and mini_word[0] == "و" and mini_word[1] == "ا" and mini_word[2] == "ل":
                mini_word = mini_word[3:]
            elif len(mini_word) > 1 and mini_word[0] == "و" and mini_word[1] == "ل" and mini_word[2] == "ل":
                mini_word = mini_word[3:]
            elif len(mini_word) > 1 and mini_word[0] == "ل" and mini_word[1] == "ل":
                mini_word = mini_word[2:]
            new_word += mini_word + " "
        _input[index] = new_word.strip()
    return _input


def desplit(array: Iterable[Any], end: str = " ") -> str:
    """
    * Takes a list full of objects, and return it as one string.
    :param array: Target list to converted to string.
    :param end: String appended after each value.
    :return: str
    """
    return end.join(str(word) for word in array if str(word))


def sanitized_and_desplited(_input: list[str] | str, replace_ي: bool = True) -> str:
    _input = _input.split() if type(_input) is str else _input
    return desplit(sanitize_language(_input, replace_ي))


def clean_file_name(name: list[str] | str) -> str:
    name = name.split() if type(name) is str else name
    caracters = ".,،<>:\"\'/\\|?*!@#$%&+^؟[]{}()~;`\\"
    ret_name = list()
    for word in name:
        mini_word = str()
        for letter in word:
            if letter not in caracters:
                mini_word += letter
        ret_name.append(mini_word)
    return desplit(ret_name, "_").lower()
