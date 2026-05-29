import datetime
import os
from pathlib import Path
from pprint import pprint
from typing import Any

import functions.functions as fs


def foo(name: str) -> str:
    pair_list = (
        ("سايق", "سائق"),
        ("سياره", "سيارة"),
        ("ونش", "ونج"),
        ("روله", "رولة"),
        ("مياة", "مياه"),
        ("ايصال", "إيصال"),
        ("امن", "أمن"),
        ("سلامه", "سلامة"),
        ("ادارة", "إدارة"),
        ("اداره", "إدارة"),
        ("ادراة", "إدارة"),
        ("اسفلت", "أسفلت"),
        ("راس", "رأس"),
        ("فرأس", "فراس"),
        ("استراح", "إستراح"),
        ("ابو", "أبو"),
        ("أبو ", "أبو"),
        ("عبد ", "عبد"),
        ("امجد", "أمجد"),
        ("انور", "أنور"),
        ("انس", "أنس"),
        ("ايهاب", "إيهاب"),
        ("ابكر", "أبكر"),
        ("بأبكر", "بابكر"),
        ("جمعه", "جمعة"),
        ("خليفه", "خليفة"),
        ("احمد", "أحمد"),
        ("على", "علي"),
        ("ابراهيم", "إبراهيم"),
        ("اسماعيل", "إسماعيل"),
        ("ادريس", "إدريس"),
        ("المولي", "المولى"),
        ("اسلام", "إسلام"),
        ("اسامة", "أسامة"),
        ("اسامه", "أسامة"),
        ("اسحاق", "إسحاق"),
        ("اسحق", "إسحاق"),
        ("اشرف", "أشرف"),
        ("ادم", "آدم"),
        ("امام", "إمام"),
        ("ايوب", "أيوب"),
        ("امين", "أمين"),
        ("ايمن", "أيمن"),
        ("يأيمن", "يامن"),
        ("الجيلى", "الجيلي"),
        ("مومن", "مؤمن"),
        ("موسي", "موسى"),
        ("مهدى", "مهدي"),
        ("مجتبي", "مجتبى"),
        ("مصطفي", "مصطفى"),
        ("مامون", "مأمون"),
        ("الدومه", "الدومة"),
        ("اواب", "أواب"),
        ("طاه", "طه"),
        ("طة", "طه"),
        ("يحى", "يحيى"),
        ("يحي", "يحيى"),
        ("يحيىى", "يحيى"),
        ("بله", "بلة"),
        ("لطفى", "لطفي"),
        ("داوود", "داؤود"),
        ("داود", "داؤود"),
        ("داؤد", "داؤود"),
        ("علا", "علاء"),
        ("علاءء", "علاء"),
        ("علاءم", "علام"),
        ("عيسي", "عيسى"),
        ("فايز", "فائز"),
        ("وايل", "وائل"),
        ("فواد", "فؤاد"),
        ("ياسن", "ياسين"),
        ("يس", "ياسين"),
        ("نياسيني", "نيسي"),
        ("مرياسينة", "مريسة"),
        ("مياسينت", "ميست"),
        ("برياسين", "بريس"),
        ("إدرياسين", "إدريس"),
        ("ونياسين", "ونيس"),
        ("مياسينر", "ميسر"),
        ("عياسينى", "عيسى"),
        ("خمياسين", "خميس"),
        ("طهر", "طاهر"),
        ("رحمه", "رحمة"),
        (" الله", "الله"),
        ("خلفالله", "خلف الله"),
        (" الدين", "الدين"),
        ("يالدين", "ي الدين"),
        ("مالدين", "م الدين"),
        ("فالدين", "ف الدين"),
        ("جالدين", "ج الدين"),
        ("خالدين", "خ الدين"),
        ("نالدين", "ن الدين"),
        ("حالدين", "ح الدين"),
        ("ذا النون", "ذوالنون"),
        ("ذو النون", "ذوالنون"),
        ("عبدالعال", "عبدالعالي"),
        ("عبدالعاليي", "عبدالعالي"),
        ("بوسف", "يوسف"),
    )
    name = fs.sanitized_and_desplited(name, replace_ي=False)


def sell_item(sold_items: list[dict], item: dict) -> dict | None:
    sold_packs, _sold_items = float(), float()
    if item["pack"]:
        str_or_float = fs.get_str_or_float("Sold Items:Packs")
        if type(str_or_float) is str and ":" in str_or_float:
            sold = str_or_float.lower().split(":")
            if not sold:
                return
            if len(sold) == 1:
                _sold_items = float(sold[0])
            else:
                sold_packs = float(sold[1])
        elif type(str_or_float) is float:
            _sold_items = str_or_float
        else:
            return
        total_sold_price = (_sold_items * item["sell-price"]) + (sold_packs * item["sell-pack-price"])
    else:
        _sold_items = float(fs.get_float("Sold Items"))
        total_sold_price = _sold_items * item["sell-price"]
    sold_item = fs.get_items(sold_items, item["serial-numbers"][0])
    if sold_item:
        left_items = item["in-stock"] - sold_item[0]["sold-items"]
        if left_items <= 0:
            print(f"Can't sell! There's {left_items} left items!")
            return
        elif _sold_items > item["in-stock"]:
            print(f"Can't sell! The demand is greater than in-stocked items. Max is {left_items}!")
            return
    _item = {
        "serial-numbers": item["serial-numbers"],
        "item-name": item["item-name"],
        "pack": item["pack"],
        "sell-price": item["sell-price"],
        "sell-pack-price": item["sell-pack-price"],
        "sold-items": _sold_items,
        "sold-packs": sold_packs,
        "total-sold-price": total_sold_price,
    }
    return _item


def get_item(
        invoice: list[dict], purchased_items: list[dict], sold_items: list[dict], str_or_float: str | float
) -> dict | None:
    is_delete = False
    if type(str_or_float) is str:
        found_items = fs.get_items(purchased_items, name=str_or_float)
        if type(found_items) is list and len(found_items) > 1:
            found_items = [(item["serial-numbers"][0], item["item-name"]) for item in found_items]
            pprint(found_items)
            return None
    else:
        if str_or_float < 0:
            str_or_float *= -1
            is_delete = True
        found_items = fs.get_items(purchased_items, str_or_float)
    if type(found_items) is list and len(found_items) == 1:
        message = f"Are you sure you want to REMOVE item: {found_items[0]['item-name']}? (Yes)"
        if is_delete and not fs.get_str(message, True):
            return delete_item(invoice, found_items[0])
        return sell_item(sold_items, found_items[0])
    pprint(found_items)
    return None


def delete_item(invoice: dict, item: dict) -> None:
    if item in invoice["items"]:
        invoice["items"].remove(item)
    invoice_path = Path(
        f"data/sales/{invoice['invoice-number']}-{fs.clean_file_name(invoice['customer']['customer-name'])}.json"
    )
    fs.dump_data(invoice, invoice_path)
    fs.clear_terminal()


def create_customer(cache: dict) -> dict[str, Any]:
    customers = fs.load_data(Path("data/customers.json"))
    while True:
        customer_name = str(fs.get_str("Customer Name"))
        name_already_exists = False
        for customer in customers:
            if fs.sanitized_and_desplited(customer_name.lower()) == fs.sanitized_and_desplited(
                customer["customer-name"].lower()
            ):
                print(f"customer name ({customer_name}) already exists!")
                name_already_exists = True
                break
        if not name_already_exists:
            customer_name = customer_name
            break

    customer_phone_numbers = list()
    while True:
        msg = (
            "Add Another Customer Phone Number? (no)"
            if customer_phone_numbers
            else "Customer Phone Number (no phone number)"
        )
        customer_phone_number = fs.get_float(msg, True)
        if not customer_phone_number:
            break
        customer_phone_numbers.append(customer_phone_number)

    cache["last-customer-number"] += 1
    customer = {
        "customer-name": customer_name,
        "customer-number": cache["last-customer-number"],
        "customer-dept": float(),
        "customer-phone-numbers": customer_phone_numbers,
    }
    customers.append(customer)
    fs.dump_data(customers, Path("data/customers.json"))
    fs.dump_data(cache, Path("data/cache/sales.json"))

    return customer


def get_customer(cache: dict) -> dict[str, Any]:
    customers = fs.load_data(Path("data/customers.json"))
    if not customers:
        return create_customer(cache)
    while True:
        str_or_float = fs.get_str_or_float("Customer Name/Number (new customer[n]/Public[ok])", True)
        if not str_or_float:
            return fs.get_items(customers, 1)[0]
        if type(str_or_float) is str:
            if str_or_float.lower() == "n":
                return create_customer(cache)
            _customers = fs.get_items(customers, name=str_or_float)
        else:
            _customers = fs.get_items(customers, str_or_float)
        if type(_customers) is list and len(_customers) == 1:
            return _customers[0]
        pprint([(customer["customer-number"], customer["customer-name"]) for customer in (_customers or customers)])


def create_invoice(cache: dict) -> dict[str, Any]:
    customer = get_customer(cache)
    invoice_number = cache["last-inovace-number"] + 1
    cache["last-inovace-number"] += 1
    cache["invoice-numbers"].append(invoice_number)
    today = datetime.date.today().isoformat()  # convert to ISO string
    return {
        "customer": customer,
        "date": str(fs.validate_date(fs.get_str(f"Inovace Date ({today})", True)) or today),
        "invoice-number": invoice_number,
        "total": float(),
        "items": list(),
    }


def get_invoice(cache: dict, saless_path: Path) -> dict | None:
    if not cache["invoice-numbers"]:
        return create_invoice(cache)
    invoice_number = fs.get_float("Invoice Number (new invoice)", True)
    if not invoice_number:
        return create_invoice(cache)
    invoice_number = int(invoice_number)
    is_delete = False
    if invoice_number < 0:
        invoice_number *= -1
        is_delete = True
    invoice_path = str()
    all_invoices = list()
    invoices = list()
    for sales_folders in saless_path.iterdir():
        for invoice_path in sales_folders.iterdir():
            if invoice_path.is_file():
                invoice = fs.load_data(invoice_path)
                all_invoices.append(invoice)
                if invoice_number == invoice["invoice-number"]:
                    invoices.append(invoice)
    if len(invoices) == 1:
        if is_delete and not fs.get_str(f"Are you sure you want to DELETE sales invoice: {invoice_number}? (Yes)", True):
            return delete_invoice(cache, invoice_path, invoice_number)
        return invoices[0]
    pprint(
        [(invoice["invoice-number"], invoice["customer"]["shorted-customer-name"]) for invoice in (invoices or all_invoices)]
    )


def delete_invoice(cache: dict, invoice_path: Path, invoice_number: int) -> None:
    if os.path.exists(invoice_path) and invoice_path.is_file():
        os.remove(invoice_path)
    cache["invoice-numbers"].remove(invoice_number)
    fs.dump_data(cache, Path("data/cache/sales.json"))
    fs.check_quit("00")


def merge_items() -> list[dict]:
    # Collect items together
    all_items = dict()
    for sales_folders in Path("data/sales").iterdir():
        for invoice_path in sales_folders.iterdir():
            if invoice_path.is_file():
                invoice = fs.load_data(invoice_path)
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
            "sell-price": float(),
            "sell-pack-price": float(),
            "sold-items": float(),
            "sold-packs": float(),
            "total-sold-price": float(),
        }
        for item in items:
            _item["item-name"] = item["item-name"]
            _item["pack"] = item["pack"]
            _item["serial-numbers"] = item["serial-numbers"]
            _item["sell-price"] = item["sell-price"]
            _item["sell-pack-price"] = item["sell-pack-price"]
            _item["sold-items"] += item["sold-items"]
            _item["sold-packs"] += item["sold-packs"]
            _item["total-sold-price"] += item["total-sold-price"]

        _items.append(_item)

    return _items


def check_out(cache: dict, invoice: dict) -> dict[str, Any]:
    while True:
        paid_price = fs.get_float(f"Paid Price ({invoice['total']})", True)
        if paid_price is None:
            paid_price = invoice["total"]
        invoice["paid-price"] = paid_price
        if paid_price < invoice['total']:
            if invoice["customer"]["customer-number"] == 1:
                print(f"{invoice['customer']['customer-name']} can't loan money!")
            else:
                invoice["customer"]["customer-dept"] += invoice['total'] - paid_price
                invoice_path = Path(
                    f"data/sales_difference/under_paied_invoices/"
                    f"{invoice['invoice-number']}-{fs.clean_file_name(invoice['customer']['customer-name'])}.json"
                )
                fs.dump_data(invoice, invoice_path)
                break
        else:
            break

    # Save items
    fs.clear_terminal()
    print("Saving items...")
    errors = list()
    if not fs.dump_data(cache, Path("data/cache/sales.json")):
        errors.append("cache")
    today = datetime.date.today().isoformat()  # convert to ISO string
    Path(f"data/sales/{today}").mkdir(exist_ok=True)
    invoice_path = Path(f"data/sales/{today}/{invoice['invoice-number']}-{fs.clean_file_name(invoice['customer']['customer-name'])}.json")
    if not fs.dump_data(invoice, invoice_path):
        errors.append("invoice")
    if errors:
        fs.get_str(f"{len(errors)} error(s) found: {fs.desplit(errors)} (continue)", True)

    fs.clear_terminal()
    print(f"Invoice Number: {invoice['invoice-number']}")
    print(f"Customer: {invoice['customer']['customer-name']}")
    print(f"Date: {invoice['date']}")
    print("Invoice Items:")
    for item in invoice["items"]:
        _ = f"{item['sold-packs']} packs and {item['sold-items']}" if item["pack"] else f"{item['sold-items']}"
        print(f"{item['serial-numbers'][0]} - {item["item-name"]}: {_} items")
    print(f"Total Price: {invoice['total']}")
    print(f"Paid Price: {paid_price}")
    if paid_price > invoice['total']:
        print(f"Return: {paid_price - invoice['total']} to {invoice['customer']['customer-name']}.")
    elif invoice["customer"]["customer-dept"] or paid_price < invoice['total']:
        print(
            f"Inform customer that {invoice['total'] - paid_price} was added to their dept.\n"
            f"And their total dept is now: {invoice["customer"]["customer-dept"]}"
        )

    return invoice
