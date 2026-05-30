import datetime
import os
from pathlib import Path
from pprint import pprint
from typing import Any

import functions.functions as fs


class PurchasesSettings(fs.Settings):
    def __init__(self):
        super().__init__()


def dump_stock_difference(self) -> bool:
    stock_difference_minus, stock_difference_plus, zero_imported_stock, zero_in_stock = (list() for _ in range(4))

    for item in merge_items(self):
        if not item["stock-difference"]:
            continue
        # zero imported stock
        if not item["imported-items"]:
            zero_imported_stock.append(item)
        # zero in stock
        elif not item["in-stock"]:
            zero_in_stock.append(item)
        # stock difference plus
        elif item["stock-difference"] > 0:
            stock_difference_plus.append(item)
        # stock difference minus
        elif item["stock-difference"] < 0:
            stock_difference_minus.append(item)

    print("\n--- Number of stock difference ---")

    # stock difference plus
    len_old_stock_difference_plus = len(fs.load_data(Path("data/stock_difference/stock_difference_plus.json")))
    print("Plus:", len_old_stock_difference_plus)
    if len(stock_difference_plus) != len_old_stock_difference_plus:
        print("New number of stock difference plus:", len(stock_difference_plus))
        fs.dump_data(stock_difference_plus, Path("data/stock_difference/stock_difference_plus.json"))

    # stock difference minus
    len_old_stock_difference_minus = len(fs.load_data(Path("data/stock_difference/stock_difference_minus.json")))
    print("Minus:", len_old_stock_difference_minus)
    if len(stock_difference_minus) != len_old_stock_difference_minus:
        print("New number of stock difference minus:", len(stock_difference_minus))
        fs.dump_data(stock_difference_minus, Path("data/stock_difference/stock_difference_minus.json"))

    # zero imported stock
    len_old_zero_imported_stock = len(fs.load_data(Path("data/stock_difference/zero_imported_stock.json")))
    print("Zero imported stock:", len_old_zero_imported_stock)
    if len(zero_imported_stock) != len_old_zero_imported_stock:
        print("New number of zero imported stock:", len(zero_imported_stock))
        fs.dump_data(zero_imported_stock, Path("data/stock_difference/zero_imported_stock.json"))

    # zero in stock
    len_old_zero_in_stock = len(fs.load_data(Path("data/stock_difference/zero_in_stock.json")))
    print("Zero in stock:", len_old_zero_in_stock)
    if len(zero_in_stock) != len_old_zero_in_stock:
        print("New number of zero in stock:", len(zero_in_stock))
        fs.dump_data(zero_in_stock, Path("data/stock_difference/zero_in_stock.json"))

    print("--- stock difference ---\n")
    if stock_difference_minus or stock_difference_plus or zero_imported_stock or zero_in_stock:
        return False
    return True


def create_serial_number(self, _dict: dict) -> bool:
    added_new_serial_number = False
    while True:
        new_serial_number = fs.get_float("Add/Remove a Serial Number? (no)", True)
        if new_serial_number:
            if new_serial_number < 0:
                if int(new_serial_number) * -1 in _dict["serial-numbers"]:
                    _dict["serial-numbers"].remove(int(new_serial_number) * -1)
            elif (
                new_serial_number not in _dict["serial-numbers"] and type(fs.get_items(self.items, new_serial_number)) is str
            ):
                _dict["serial-numbers"].append(int(new_serial_number))
            added_new_serial_number = True
        else:
            break
    if added_new_serial_number:
        pprint(_dict)
        return True
    return False


def create_supplier(self) -> dict[str, Any]:
    extra_str = (
        "شركه صاله بىع لبىع تعبئه تحمىص اجود انواع مواد غذائى غذائىه شوكولاطه شوكولاته حلوى "
        "حلوىات بقولىات توابل مكسرات تمر تمور عطر عطور تنظىف نظافه جمله قطاعى نقدا"
    )
    suppliers = fs.load_data(Path("data/suppliers.json"))
    while True:
        supplier_name = str(fs.get_str("Supplier Name"))
        name_already_exists = False
        for supplier in suppliers:
            if fs.sanitized_and_desplited(supplier_name.lower()) == fs.sanitized_and_desplited(
                supplier["supplier-name"].lower()
            ):
                print(f"Supplier name ({supplier_name}) already exists!")
                name_already_exists = True
                break
        if not name_already_exists:
            supplier_name = supplier_name.split()
            break

    shorted_supplier_name = list()
    sanitized_supplier = fs.sanitized_and_desplited(supplier_name.copy())

    for index, word in enumerate(sanitized_supplier.split()):
        if word not in extra_str:
            shorted_supplier_name.append(supplier_name[index])

    self.cache["last-supplier-number"] += 1
    supplier = {
        "supplier-name": fs.desplit(supplier_name),
        "shorted-supplier-name": fs.clean_file_name(shorted_supplier_name),
        "supplier-number": self.cache["last-supplier-number"],
    }
    suppliers.append(supplier)
    fs.dump_data(suppliers, Path("data/suppliers.json"))
    fs.dump_data(self.cache, Path("data/cache/purchases.json"))

    return supplier


def get_supplier(self) -> dict[str, Any]:
    suppliers = fs.load_data(Path("data/suppliers.json"))
    if not suppliers:
        return create_supplier(self)
    while True:
        str_or_float = fs.get_str_or_float("Supplier Name/Number (new supplier)", True)
        if not str_or_float:
            return create_supplier(self)
        if type(str_or_float) is str:
            _suppliers = fs.get_items(suppliers, name=str_or_float)
        else:
            _suppliers = fs.get_items(suppliers, str_or_float)
        if type(_suppliers) is list and len(_suppliers) == 1:
            return _suppliers[0]
        pprint([(supplier["supplier-number"], supplier["supplier-name"]) for supplier in (_suppliers or suppliers)])


def create_item(self, serial_number: int) -> dict[str, Any]:
    while True:
        name = fs.get_str("Item Name")
        name_already_exists = False
        for item in self.items:
            if fs.sanitized_and_desplited(name.lower()) == fs.sanitized_and_desplited(item["item-name"].lower()):
                print(f"Item name ({name}) already exists!")
                name_already_exists = True
                break
        if not name_already_exists:
            break
    pack = fs.get_float("Pack (no pack)", True)
    imported_packs = None
    if pack is not None:
        imported_packs = float(fs.get_float("Imported Packs"))
        imported = imported_packs * pack
    else:
        imported = float(fs.get_float("Imported Items"))
    in_stock = fs.get_float(f"In-Stock Items ({imported})", True)
    in_stock = in_stock if in_stock is not None else imported
    purchase_pack_price = None
    if pack is not None:
        purchase_pack_price = float(fs.get_float("Purchase pack Price"))
        purchase_price = purchase_pack_price / pack
    else:  # self.settings.profit, self.settings.divide
        purchase_price = float(fs.get_float("Purchase Price"))
    profit = float(self.calculate_profit(purchase_price))
    sell_price = fs.get_float(f"Sell Price ({purchase_price} -> {profit})", True)
    sell_price = sell_price if sell_price is not None else profit
    sell_pack_price = None
    if purchase_pack_price:
        pack_profit = float(self.calculate_profit(purchase_pack_price))
        sell_pack_price = fs.get_float(f"Sell Pack Price ({purchase_pack_price} -> {pack_profit})", True)
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
        "total-purchase-price": purchase_price * imported,
        "stock-difference": in_stock - imported,
    }
    self.items.append(item)
    create_serial_number(self, item)
    return item


def get_item(self) -> tuple[dict | None, str]:
    serial_number = int()
    str_or_float = fs.get_str_or_float("Item Name/Serial Number (*)", True)
    if not str_or_float:
        self.cache["last-barcode-number"] += 1
        return create_item(self, self.cache["last-barcode-number"]), "create"
    is_delete = False
    if type(str_or_float) is str:
        found_items = fs.get_items(self.items, name=str_or_float)
        if type(found_items) is list and len(found_items) > 1:
            found_items = [(item["serial-numbers"][0], item["item-name"]) for item in found_items]
            pprint(found_items)
            return None, str()
    else:
        if str_or_float < 0:
            str_or_float *= -1
            is_delete = True
        found_items = fs.get_items(self.items, str_or_float)
        serial_number = int(str_or_float)
    if type(found_items) is list and len(found_items) == 1:
        message = f"Are you sure you want to REMOVE item: {found_items[0]['item-name']}? (Yes)"
        if is_delete and not fs.get_str(message, True):
            return delete_item(self, found_items[0]), str()
        return found_items[0], "get"
    if serial_number:
        return create_item(self, serial_number), "create"
    return None, str()


def update_item(self, item: dict) -> dict[str, Any]:
    pack = item["pack"]
    imported_packs = None
    if pack is not None:
        imported_packs = fs.get_float("Imported Packs")
        imported = imported_packs * pack
    else:
        imported = fs.get_float("Imported Items")
    in_stock = fs.get_float(f"In-Stock Items ({imported})", True) or imported
    purchase_pack_price = None
    if pack is not None:
        purchase_pack_price = (
            fs.get_float(f"Purchase pack Price ({item["purchase-pack-price"]})", True) or item["purchase-pack-price"]
        )
        purchase_price = purchase_pack_price / pack
    else:
        purchase_price = fs.get_float(f"Purchase Price ({item["purchase-price"]})", True) or item["purchase-price"]
    if purchase_price != item["purchase-price"]:
        profit = self.calculate_profit(purchase_price)
        sell_price = fs.get_float(f"Sell Price ({purchase_price} -> {profit})", True) or profit
        pack_profit = self.calculate_profit(purchase_pack_price)
        sell_pack_price = fs.get_float(f"Sell Pack Price ({purchase_pack_price} -> {pack_profit})", True) or pack_profit
    else:
        sell_price = fs.get_float(f"Sell Price ({item["sell-price"]})", True) or item["sell-price"]
        sell_pack_price = fs.get_float(f"Sell Pack Price ({item["sell-pack-price"]})", True) or item["sell-pack-price"]
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
        "total-purchase-price": (
            (purchase_pack_price * imported_packs)
            if (imported_packs and purchase_pack_price)
            else (purchase_price * imported)
        ),
        "stock-difference": in_stock - imported,
    }
    items = list()
    for item in self.items:
        if _item["serial-numbers"][0] not in item["serial-numbers"]:
            items.append(item)
    items.append(_item)
    self.items = items
    create_serial_number(self, _item)
    return _item


def delete_item(self, item: dict) -> None:
    if item in self.invoice["items"]:
        self.invoice["items"].remove(item)
    fs.dump_data(self.invoice, self.invoice_path)
    dump_stock_difference(self)
    fs.clear_terminal()


def add_to_item(self, item: dict) -> dict[str, Any]:
    pack = item["pack"]
    imported_packs = None
    if pack is not None:
        imported_packs = fs.get_float("Imported Packs")
        imported = imported_packs * pack
    else:
        imported = fs.get_float("Imported Items")
    in_stock = (fs.get_float(f"In-Stock Items ({imported})", True) or imported) + item["in-stock"]
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
        "total-purchase-price": (
            (item["purchase-pack-price"] * imported_packs)
            if (imported_packs and item["purchase-pack-price"])
            else (item["purchase-price"] * imported)
        ),
        "stock-difference": in_stock - imported,
    }
    for __item in self.items:
        if _item["serial-numbers"][0] in __item["serial-numbers"]:
            self.items.remove(__item)
            self.items.append(_item)
            break
    create_serial_number(self, _item)
    return _item


def create_invoice(self) -> dict[str, Any]:
    supplier_invoice_number = fs.get_float("Supplier Invoice Number (no number)", True)
    supplier = get_supplier(self)
    invoice_number = self.cache["last-inovace-number"] + 1
    self.cache["last-inovace-number"] += 1
    self.cache["invoice-numbers"].append(invoice_number)
    today = datetime.date.today().isoformat()  # convert to ISO string
    return {
        "supplier": supplier,
        "date": str(fs.validate_date(fs.get_str(f"Inovace Date ({today})", True)) or today),
        "invoice-number": invoice_number,
        "supplier-invoice-number": supplier_invoice_number,
        "items": list(),
    }


def get_invoice(self) -> dict | None:
    if not self.cache["invoice-numbers"]:
        return create_invoice(self)
    invoice_number = fs.get_float("Invoice Number (new invoice)", True)
    if not invoice_number:
        return create_invoice(self)
    invoice_number = int(invoice_number)
    is_delete = False
    if invoice_number < 0:
        invoice_number *= -1
        is_delete = True
    invoice_path = str()
    all_invoices = list()
    invoices = list()
    for invoice_path in self.purchases_path.iterdir():
        if invoice_path.is_file():
            invoice = fs.load_data(invoice_path)
            all_invoices.append(invoice)
            if invoice_number == invoice["invoice-number"]:
                invoices.append(invoice)
    if len(invoices) == 1:
        if is_delete and not fs.get_str(f"Are you sure you want to DELETE purchase invoice: {invoice_number}? (Yes)", True):
            return delete_invoice(self, invoice_path, invoice_number)
        return invoices[0]
    pprint(
        [(invoice["invoice-number"], invoice["supplier"]["shorted-supplier-name"]) for invoice in (invoices or all_invoices)]
    )


def merge_items(self) -> list[dict]:
    # Collect items together
    all_items = dict()
    for invoice_path in self.purchases_path.iterdir():
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
            "imported-items": float(),
            "imported-packs": float(),
            "in-stock": float(),
            "purchase-pack-price": float(),
            "purchase-price": float(),
            "sell-price": float(),
            "sell-pack-price": float(),
            "total-purchase-price": float(),
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
            _item["purchase-price"] = fs.normalize_price(self, purchase_price / imported_items)
            _item["sell-price"] = fs.normalize_price(self, sell_price / imported_items)

            if item["pack"]:
                imported_packs += item["imported-packs"]
                purchase_pack_price += item["purchase-pack-price"] * item["imported-packs"]
                sell_pack_price += item["sell-pack-price"] * item["imported-packs"]
                _item["imported-packs"] += item["imported-packs"]
                _item["purchase-pack-price"] = fs.normalize_price(self, purchase_pack_price / imported_packs)
                _item["sell-pack-price"] = fs.normalize_price(self, sell_pack_price / imported_packs)
            else:
                _item["purchase-pack-price"], _item["sell-pack-price"], _item["imported-packs"] = 3 * (None,)

            _item["in-stock"] += item["in-stock"]
            _item["stock-difference"] = _item["in-stock"] - _item["imported-items"]
            _item["total-purchase-price"] = (
                (item["purchase-pack-price"] * _item["imported-packs"])
                if (_item["imported-packs"] and item["purchase-pack-price"])
                else (item["purchase-price"] * _item["imported-items"])
            )

        _items.append(_item)

    return _items


def delete_invoice(self, invoice_path: Path, invoice_number: int) -> None:
    if os.path.exists(invoice_path) and invoice_path.is_file():
        os.remove(invoice_path)
    self.cache["invoice-numbers"].remove(invoice_number)
    dump_stock_difference(self)
    fs.dump_data(self.cache, Path("data/cache/purchases.json"))
    fs.check_quit("00")
