import datetime
import json
import math
import os
import re
from pathlib import Path
from pprint import pprint


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


def normalize_price(price: float, divide: float) -> float:
    """
    * Round price UP to the nearest divide step.
    :parm price: Price to be normalized.
    :parm divide: The point to which price to be normalized.
    """
    if divide <= 0:
        raise ValueError("divide must be greater than 0")

    normalized = math.ceil(price / divide) * divide

    # Avoid floating-point artifacts like 3.50000000004
    return round(normalized, 10)


_list = list()


def notes(_input: float, value: float) -> None:
    if _list:
        if len(_list) <= 5:
            print("History:")
            for key, pair in _list:
                print(f"{key} -> {pair:.2f}")
        else:
            print("History (last 5 calculations):")
            for key, pair in _list[-5:]:
                print(f"{key} -> {pair:.2f}")
        print("\nResult:")
    else:
        print("Result:")
    _list.append((_input, value))


def clear_terminal():
    # 'nt' is for Windows, 'posix' covers Linux and macOS
    os.system('cls' if os.name == 'nt' else 'clear')


def check_quit(_input, kill_process: bool = True):
    if _input.lower() in ['q', 'quit', 'e', 'exit', 'l', 'leave', '00']:
        clear_terminal()
        if kill_process:
            quit()
        return True
    return False


def get_float(name: str = str(), allow_blink: bool = False) -> float | None:
    while True:
        try:
            _input = input(f'({name}) >>> ').strip()
            if not _input:
                if allow_blink:
                    return
                continue
            if check_quit(_input):
                return
            return float(_input)
        except Exception as e:
            print('Error', e)


def get_str(name: str = str(), allow_blink: bool = False) -> str | None:
    while True:
        try:
            _input = input(f'({name}) >>> ').strip()
            if not _input:
                if allow_blink:
                    return
                continue
            if check_quit(_input):
                return
            return _input
        except Exception as e:
            print('Error', e)


def get_str_or_float(name: str = str(), allow_blink: bool = False) -> str | float | None:
    while True:
        try:
            _input = input(f'({name}) >>> ').strip()
            if not _input:
                if allow_blink:
                    return
                continue
            if check_quit(_input):
                return
            return float(_input)
        except ValueError:
            return _input
        except Exception as e:
            print('Error', e)


def load_data(file_path: str = "data/data.json"):
    with open(file_path, 'r') as file_path:
        return json.load(file_path)


def dump_data(data, file_path: str = "data/data.json") -> bool:
    try:
        if not Path(file_path).exists():
            Path(file_path).write_text(json.dumps({}, indent=4))
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            return True
    except Exception as e:
        print('Error', e)
        return False


def get_data(data: list[dict], serial_number: int = int, name: str = str()) -> list[dict] | str:
    ret_list = list()
    try:
        for _dict in data:
            if serial_number and serial_number in _dict['serial-numbers']:
                ret_list.append(_dict)
            if name and (
                name.lower() in _dict['name'].lower().split()
                or name.lower() == _dict['name'].lower()
                or name.lower() in _dict['name'].lower()
            ):
                ret_list.append(_dict)
        if ret_list:
            return ret_list
        raise KeyError('No match')
    except KeyError as e:
        return f'Error {e}'


def dump_stock_difference(data: list[dict]):
    stock_difference_minus, stock_difference_plus, zero_imported_stock, zero_in_stock = (list() for _ in range(4))

    try:
        for _dict in data:
            if not _dict['stock-difference']:
                continue
            # zero imported stock
            if not _dict["imported"]:
                zero_imported_stock.append(_dict)
            # zero in stock
            elif not _dict["in-stock"]:
                zero_in_stock.append(_dict)
            # stock difference plus
            elif _dict['stock-difference'] > 0:
                stock_difference_plus.append(_dict)
            # stock difference minus
            elif _dict['stock-difference'] < 0:
                stock_difference_minus.append(_dict)
    except KeyError as e:
        print('Error', e)

    print("--- \nNumber of stock difference ---")

    # stock difference plus
    len_old_stock_difference_plus = len(load_data("data/stock_difference/stock_difference_plus.json"))
    print('Plus:', len_old_stock_difference_plus)
    if len(stock_difference_plus) != len_old_stock_difference_plus:
        print('New number of stock difference plus:', len(stock_difference_plus))
        dump_data(stock_difference_plus, 'json/stock_difference/stock_difference_plus.json')

    # stock difference minus
    len_old_stock_difference_minus = len(load_data("data/stock_difference/stock_difference_minus.json"))
    print('Minus:', len_old_stock_difference_minus)
    if len(stock_difference_minus) != len_old_stock_difference_minus:
        print('New number of stock difference minus:', len(stock_difference_minus))
        dump_data(stock_difference_minus, 'json/stock_difference/stock_difference_minus.json')

    # zero imported stock
    len_old_zero_imported_stock = len(load_data("data/stock_difference/zero_imported_stock.json"))
    print('Zero imported stock:', len_old_zero_imported_stock)
    if len(zero_imported_stock) != len_old_zero_imported_stock:
        print('New number of zero imported stock:', len(zero_imported_stock))
        dump_data(zero_imported_stock, 'json/stock_difference/zero_imported_stock.json')

    # zero in stock
    len_old_zero_in_stock = len(load_data("data/stock_difference/zero_in_stock.json"))
    print('Zero in stock:', len_old_zero_in_stock)
    if len(zero_in_stock) != len_old_zero_in_stock:
        print('New number of zero in stock:', len(zero_in_stock))
        dump_data(zero_in_stock, 'json/stock_difference/zero_in_stock.json')

    print("---\n")


def add_new_serial_number(data, _dict: dict) -> bool:
    added_new_serial_number = False
    while True:
        new_serial_number = get_float('Add/Remove a Serial Number? (no)', True)
        if new_serial_number:
            if new_serial_number < 0:
                if int(new_serial_number) * -1 in _dict['serial-numbers']:
                    _dict['serial-numbers'].remove(int(new_serial_number) * -1)
            elif new_serial_number not in _dict['serial-numbers'] and type(get_data(data, new_serial_number)) is str:
                _dict['serial-numbers'].append(int(new_serial_number))
            added_new_serial_number = True
        else:
            break
    if added_new_serial_number:
        pprint(_dict)
        return True
    return False
