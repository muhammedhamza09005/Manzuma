import datetime
import json
import math
import os
import re
from datetime import date
from pathlib import Path
from pprint import pprint
from typing import Any, Iterable

from calculate_profit import calculate_profit


class ManzumaException(Exception):
    """Custom exception class with a message."""

    def __init__(self, message: str = str()):
        self.message = message
        super().__init__(self.message)


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


def load_data(file_path: Path = Path("data/items.json")):
    with open(file_path, "r", encoding="utf-8") as file_path:
        return json.load(file_path)


def dump_data(data, file_path: Path = Path("data/items.json")) -> bool:
    if not Path(file_path).exists():
        Path(file_path).write_text(json.dumps({}, indent=4))
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    return False


def get_items(data: list[dict], numbers: int | float = int, name: str = str()) -> list[dict]:
    ret_list = list()
    if not data:
        print("get_items error: not data")
        return ret_list
    numbers_key = (
        "serial-numbers" if "serial-numbers" in data[0] else "supplier-number" if "supplier-number" in data[0] else str()
    )
    name_key = "item-name" if "item-name" in data[0] else "supplier-name" if "supplier-name" in data[0] else str()
    if not numbers_key:
        print("get_items error: numbers_key KeyError")
        return ret_list
    if not name_key:
        print("get_items error: name_key KeyError")
        return ret_list
    name = desplit(sanitize_language(name.lower().split()))
    for _dict in data:
        dict_name = desplit(sanitize_language(_dict[name_key].lower().split()))
        if numbers and type(_dict[numbers_key]) is list and numbers in _dict[numbers_key]:
            return [_dict]
        if numbers and type(_dict[numbers_key]) in [int, float] and numbers == _dict[numbers_key]:
            return [_dict]
        if name and name in dict_name.split() or name == dict_name or name in dict_name:
            ret_list.append(_dict)
    return ret_list


def dump_stock_difference(data: list[dict]) -> bool:
    stock_difference_minus, stock_difference_plus, zero_imported_stock, zero_in_stock = (list() for _ in range(4))

    for _dict in data:
        if not _dict["stock-difference"]:
            continue
        # zero imported stock
        if not _dict["imported-items"]:
            zero_imported_stock.append(_dict)
        # zero in stock
        elif not _dict["in-stock"]:
            zero_in_stock.append(_dict)
        # stock difference plus
        elif _dict["stock-difference"] > 0:
            stock_difference_plus.append(_dict)
        # stock difference minus
        elif _dict["stock-difference"] < 0:
            stock_difference_minus.append(_dict)

    print("\n--- Number of stock difference ---")

    # stock difference plus
    len_old_stock_difference_plus = len(load_data(Path("data/stock_difference/stock_difference_plus.json")))
    print("Plus:", len_old_stock_difference_plus)
    if len(stock_difference_plus) != len_old_stock_difference_plus:
        print("New number of stock difference plus:", len(stock_difference_plus))
        dump_data(stock_difference_plus, Path("data/stock_difference/stock_difference_plus.json"))

    # stock difference minus
    len_old_stock_difference_minus = len(load_data(Path("data/stock_difference/stock_difference_minus.json")))
    print("Minus:", len_old_stock_difference_minus)
    if len(stock_difference_minus) != len_old_stock_difference_minus:
        print("New number of stock difference minus:", len(stock_difference_minus))
        dump_data(stock_difference_minus, Path("data/stock_difference/stock_difference_minus.json"))

    # zero imported stock
    len_old_zero_imported_stock = len(load_data(Path("data/stock_difference/zero_imported_stock.json")))
    print("Zero imported stock:", len_old_zero_imported_stock)
    if len(zero_imported_stock) != len_old_zero_imported_stock:
        print("New number of zero imported stock:", len(zero_imported_stock))
        dump_data(zero_imported_stock, Path("data/stock_difference/zero_imported_stock.json"))

    # zero in stock
    len_old_zero_in_stock = len(load_data(Path("data/stock_difference/zero_in_stock.json")))
    print("Zero in stock:", len_old_zero_in_stock)
    if len(zero_in_stock) != len_old_zero_in_stock:
        print("New number of zero in stock:", len(zero_in_stock))
        dump_data(zero_in_stock, Path("data/stock_difference/zero_in_stock.json"))

    print("--- stock difference ---\n")
    if (stock_difference_minus or stock_difference_plus or zero_imported_stock or zero_in_stock):
        return False
    return True


def create_serial_number(data, _dict: dict) -> bool:
    added_new_serial_number = False
    while True:
        new_serial_number = get_float("Add/Remove a Serial Number? (no)", True)
        if new_serial_number:
            if new_serial_number < 0:
                if int(new_serial_number) * -1 in _dict["serial-numbers"]:
                    _dict["serial-numbers"].remove(int(new_serial_number) * -1)
            elif new_serial_number not in _dict["serial-numbers"] and type(get_items(data, new_serial_number)) is str:
                _dict["serial-numbers"].append(int(new_serial_number))
            added_new_serial_number = True
        else:
            break
    if added_new_serial_number:
        pprint(_dict)
        return True
    return False


def create_purchase_item(items: list[dict], serial_number: int) -> dict[str, Any]:
    while True:
        name = get_str("Item Name")
        name_already_exists = False
        for item in items:
            if name.lower() == item["item-name"].lower():
                print(f"Item name ({name}) already exists!")
                name_already_exists = True
                break
        if not name_already_exists:
            break
    pack = get_float("Pack (no pack)", True)
    imported_packs = None
    if pack is not None:
        imported_packs = float(get_float("Imported Packs"))
        imported = imported_packs * pack
    else:
        imported = float(get_float("Imported Items"))
    in_stock = get_float(f"In-Stock Items ({imported})", True)
    in_stock = in_stock if in_stock is not None else imported
    purchase_pack_price = None
    if pack is not None:
        purchase_pack_price = get_float("Purchase pack Price")
        purchase_price = purchase_pack_price / pack
    else:
        purchase_price = get_float("Purchase Price")
    profit = float(calculate_profit(10, 0.25, purchase_price))
    sell_price = get_float(f"Sell Price ({purchase_price} -> {profit})", True)
    sell_price = sell_price if sell_price is not None else profit
    sell_pack_price = None
    if purchase_pack_price:
        pack_profit = float(calculate_profit(10, 0.25, purchase_pack_price))
        sell_pack_price = get_float(f"Sell Pack Price ({purchase_pack_price} -> {pack_profit})", True)
        sell_pack_price = sell_pack_price if sell_pack_price is not None else pack_profit
    item = {
        "serial-numbers": [serial_number],
        "item-name": name,
        "pack": pack,
        "imported-items": imported,
        "imported-packs": imported_packs,
        "in-stock": in_stock,
        "purchase-pack-price": purchase_pack_price,
        "purchase-price": purchase_price,
        "sell-price": sell_price,
        "sell-pack-price": sell_pack_price,
        "total-price": purchase_price * imported,
        "stock-difference": in_stock - imported,
    }
    items.append(item)
    create_serial_number(items, item)
    return item


def update_purchase_item(data: list[dict], item: dict) -> dict[str, Any]:
    pack = item["pack"]
    imported_packs = None
    if pack is not None:
        imported_packs = get_float("Imported Packs")
        imported = imported_packs * pack
    else:
        imported = get_float("Imported Items")
    in_stock = get_float(f"In-Stock Items ({imported})", True) or imported
    purchase_pack_price = None
    if pack is not None:
        purchase_pack_price = (
            get_float(f"Purchase pack Price ({item["purchase-pack-price"]})", True) or item["purchase-pack-price"]
        )
        purchase_price = purchase_pack_price / pack
    else:
        purchase_price = get_float(f"Purchase Price ({item["purchase-price"]})", True) or item["purchase-price"]
    if purchase_price != item["purchase-price"]:
        profit = calculate_profit(10, 0.25, purchase_price)
        sell_price = get_float(f"Sell Price ({purchase_price} -> {profit})", True) or profit
        pack_profit = calculate_profit(10, 0.25, purchase_pack_price)
        sell_pack_price = get_float(f"Sell Pack Price ({purchase_pack_price} -> {pack_profit})", True) or pack_profit
    else:
        sell_price = get_float(f"Sell Price ({item["sell-price"]})", True) or item["sell-price"]
        sell_pack_price = get_float(f"Sell Pack Price ({item["sell-pack-price"]})", True) or item["sell-pack-price"]
    _item = {
        "serial-numbers": item["serial-numbers"],
        "item-name": item["item-name"],
        "pack": pack,
        "imported-items": imported,
        "imported-packs": imported_packs,
        "in-stock": in_stock,
        "purchase-pack-price": purchase_pack_price,
        "purchase-price": purchase_price,
        "sell-price": sell_price,
        "sell-pack-price": sell_pack_price,
        "total-price": (
            (purchase_pack_price * imported_packs)
            if (imported_packs and purchase_pack_price)
            else (purchase_price * imported)
        ),
        "stock-difference": in_stock - imported,
    }
    _data = list()
    for _dict in load_data():
        if _item["serial-numbers"][0] not in _dict["serial-numbers"]:
            _data.append(_dict)
    _data.append(_item)
    data = _data
    create_serial_number(data, _item)
    return _item


def add_to_item(data: list[dict], item: dict) -> dict[str, Any]:
    pack = item["pack"]
    imported_packs = None
    if pack is not None:
        imported_packs = get_float("Imported Packs")
        imported = imported_packs * pack
    else:
        imported = get_float("Imported Items")
    in_stock = (get_float(f"In-Stock Items ({imported})", True) or imported) + item["in-stock"]
    if imported_packs:
        imported_packs += item["imported-packs"]
    imported += item["imported-items"]
    _item = {
        "serial-numbers": item["serial-numbers"],
        "item-name": item["item-name"],
        "pack": pack,
        "imported-items": imported,
        "imported-packs": imported_packs,
        "in-stock": in_stock,
        "purchase-pack-price": item["purchase-pack-price"],
        "purchase-price": item["purchase-price"],
        "sell-price": item["sell-price"],
        "sell-pack-price": item["sell-pack-price"],
        "total-price": (
            (item["purchase-pack-price"] * imported_packs)
            if (imported_packs and item["purchase-pack-price"])
            else (item["purchase-price"] * imported)
        ),
        "stock-difference": in_stock - imported,
    }
    for _dict in data:
        if _item["serial-numbers"][0] in _dict["serial-numbers"]:
            data.remove(_dict)
            data.append(_item)
            break
    create_serial_number(data, _item)
    return _item


def sanitize_language(_input: list[str]) -> list[str]:
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
                elif letter == "ؤ":
                    mini_word += "و"
                elif letter == "ي":
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


def clean_file_name(name: list[str]) -> str:
    caracters = ".,،<>:\"\'/\\|?*!@#$%&+^؟[]{}()~;`\\"
    ret_name = list()
    for word in name:
        mini_word = str()
        for letter in word:
            if not letter in caracters:
                mini_word += letter
        ret_name.append(mini_word)
    return desplit(ret_name, "_")


def create_supplier(cache: dict) -> dict[str, Any]:
    extra_str = (
        "شركه صاله بىع لبىع تعبئه تحمىص اجود انواع مواد غذائى غذائىه شوكولاطه شوكولاته حلوى "
        "حلوىات بقولىات توابل مكسرات تمر تمور عطر عطور تنظىف نظافه جمله قطاعى نقدا"
    )
    suppliers = load_data(Path("data/suppliers.json"))
    while True:
        supplier_name = str(get_str("Supplier Name"))
        name_already_exists = False
        for supplier in suppliers:
            if supplier_name.lower() == supplier["supplier-name"].lower():
                print(f"Supplier name ({supplier_name}) already exists!")
                name_already_exists = True
                break
        if not name_already_exists:
            supplier_name = supplier_name.split()
            break

    shorted_supplier_name = list()
    sanitized_supplier = desplit(sanitize_language(supplier_name.copy()))

    for index, word in enumerate(sanitized_supplier.split()):
        if word not in extra_str:
            shorted_supplier_name.append(supplier_name[index])

    cache["last-supplier-number"] += 1
    supplier = {
        "supplier-name": desplit(supplier_name),
        "shorted-supplier-name": clean_file_name(shorted_supplier_name),
        "supplier-number": cache["last-supplier-number"],
    }
    suppliers.append(supplier)
    dump_data(suppliers, Path("data/suppliers.json"))
    dump_data(cache, Path("data/cache.json"))

    return supplier


def get_supplier(cache: dict) -> dict[str, Any]:
    suppliers = load_data(Path("data/suppliers.json"))
    if not suppliers:
        return create_supplier(cache)
    while True:
        str_or_float = get_str_or_float("Supplier Name/Number (new supplier)", True)
        if not str_or_float:
            return create_supplier(cache)
        if type(str_or_float) is str:
            _suppliers = get_items(suppliers, name=str_or_float)
        else:
            _suppliers = get_items(suppliers, str_or_float)
        if type(_suppliers) is list and len(_suppliers) == 1:
            return _suppliers[0]
        pprint([(supplier["supplier-number"], supplier["supplier-name"]) for supplier in (_suppliers or suppliers)])


def create_purchase_invoice(cache: dict) -> dict[str, Any]:
    supplier_invoice_number = int(get_float("Supplier Invoice Number"))
    supplier = get_supplier(cache)
    invoice_number = cache["last-purchase-inovace-number"] + 1
    cache["last-purchase-inovace-number"] += 1
    cache["purchase-invoice-numbers"].append(invoice_number)
    today = date.today().isoformat()  # convert to ISO string
    return {
        "supplier": supplier,
        "date": str(validate_date(get_str(f"Inovace Date ({today})", True)) or today),
        "invoice-number": invoice_number,
        "supplier-invoice-number": supplier_invoice_number,
        "items": list(),
    }


def get_purchase_invoice(cache: dict, purchases_path: Path) -> dict | None:
    if not cache["purchase-invoice-numbers"]:
        return create_purchase_invoice(cache)
    invoice_number = get_float("Invoice Number (new invoice)", True)
    if not invoice_number:
        return create_purchase_invoice(cache)
    invoice_number = int(invoice_number)
    is_delete = False
    if invoice_number < 0:
        invoice_number *= -1
        is_delete = True
    invoice_path = str()
    all_invoices = list()
    invoices = list()
    for invoice_path in purchases_path.iterdir():
        if invoice_path.is_file():
            invoice = load_data(invoice_path)
            all_invoices.append(invoice)
            if invoice_number == invoice["invoice-number"]:
                invoices.append(invoice)
    if len(invoices) == 1:
        if is_delete and not get_str(f"Are you sure you want to DELETE purchase invoice: {invoice_number}? (Yes)", True):
            return delete_purchase_invoice(cache, invoice_path, invoice_number)
        return invoices[0]
    pprint(
        [
            (invoice["invoice-number"], invoice["supplier"]["shorted-supplier-name"])
            for invoice in (invoices or all_invoices)
        ]
    )


def get_purchase_item(invoice: list[dict], items: list[dict], cache: dict) -> tuple[dict | None, str]:
    serial_number = int()
    str_or_float = get_str_or_float("Item Name / Serial Number (*)", True)
    if not str_or_float:
        cache["last-barcode-number"] += 1
        return create_purchase_item(items, cache["last-barcode-number"]), "create"
    is_delete = False
    if type(str_or_float) is str:
        invoice_items = get_items(items, name=str_or_float)
        if type(invoice_items) is list and len(invoice_items) > 1:
            invoice_items = [(item["serial-numbers"][0], item["item-name"]) for item in invoice_items]
            pprint(invoice_items)
            return None, str()
    else:
        if str_or_float < 0:
            str_or_float *= -1
            is_delete = True
        invoice_items = get_items(items, str_or_float)
        serial_number = int(str_or_float)
    if type(invoice_items) is list and len(invoice_items) == 1:
        message = f"Are you sure you want to REMOVE item: {invoice_items[0]['item-name']}? (Yes)"
        if is_delete and not get_str(message, True):
            return delete_purchase_item(invoice, invoice_items[0]), str()
        return invoice_items[0], "get"
    if serial_number:
        return create_purchase_item(items, serial_number), "create"
    return None, str()


def merge_purchases_items() -> list[dict]:
    # Collect items together
    all_items = dict()
    for invoice_path in Path("data/purchases").iterdir():
        if invoice_path.is_file():
            invoice = load_data(invoice_path)
            for item in invoice["items"]:
                try:
                    all_items[item["serial-numbers"][0]].append(item)
                except KeyError:
                    all_items[item["serial-numbers"][0]] = [item]

    # Merge items together
    _items = list()
    for _, items in all_items.items():
        if len(items) == 1:
            _items.append(items[0])
            continue

        _item = {
            "serial-numbers": list(),
            "item-name": str(),
            "pack": float(),
            "imported-items": float(),
            "imported-packs": float(),
            "in-stock": float(),
            "purchase-pack-price": float(),
            "purchase-price": float(),
            "sell-price": float(),
            "sell-pack-price": float(),
            "total-price": float(),
            "stock-difference": float(),
        }
        imported_items, purchase_price, sell_price = int(), int(), int()
        imported_packs, purchase_pack_price, sell_pack_price = int(), int(), int()
        for item in items:
            _item["item-name"] = item["item-name"]
            _item["pack"] = item["pack"]
            _item["serial-numbers"] = item["serial-numbers"]

            imported_items += item["imported-items"]
            purchase_price += item["purchase-price"] * item["imported-items"]
            sell_price += item["sell-price"] * item["imported-items"]
            _item["imported-items"] += item["imported-items"]
            _item["purchase-price"] = normalize_price(purchase_price / imported_items, 0.25)
            _item["sell-price"] = normalize_price(sell_price / imported_items, 0.25)

            if item["pack"]:
                imported_packs += item["imported-packs"]
                purchase_pack_price += item["purchase-pack-price"] * item["imported-packs"]
                sell_pack_price += item["sell-pack-price"] * item["imported-packs"]
                _item["imported-packs"] += item["imported-packs"]
                _item["purchase-pack-price"] = normalize_price(purchase_pack_price / imported_packs, 0.25)
                _item["sell-pack-price"] = normalize_price(sell_pack_price / imported_packs, 0.25)
            else:
                _item["purchase-pack-price"], _item["sell-pack-price"], _item["imported-packs"] = 3 * (None,)

            _item["in-stock"] += item["in-stock"]
            _item["stock-difference"] = _item["in-stock"] - _item["imported-items"]
            _item["total-price"] = (
                (item["purchase-pack-price"] * _item["imported-packs"])
                if (_item["imported-packs"] and item["purchase-pack-price"])
                else (item["purchase-price"] * _item["imported-items"])
            )

        _items.append(_item)

    return _items


def delete_purchase_invoice(cache: dict, invoice_path: Path, invoice_number: int) -> None:
    if os.path.exists(invoice_path) and invoice_path.is_file():
        os.remove(invoice_path)
    cache["purchase-invoice-numbers"].remove(invoice_number)
    items = merge_purchases_items()
    dump_data(items)
    dump_stock_difference(items)
    dump_data(cache, Path("data/cache.json"))
    check_quit("00")


def delete_purchase_item(invoice: dict, item: dict) -> None:
    if item in invoice["items"]:
        invoice["items"].remove(item)
    path = f"{Path('data/purchases')}/{invoice['invoice-number']}-{invoice['supplier']['shorted-supplier-name']}.json"
    dump_data(invoice, path)
    items = merge_purchases_items()
    dump_data(items)
    dump_stock_difference(items)
    clear_terminal()
