from pathlib import Path
from pprint import pprint
from typing import Any

import functions.functions as fs
import functions.sales_functions as sfs


def sales() -> dict[str, Any]:
    # init sales
    fs.clear_terminal()
    print("Loding sales...")
    items = fs.load_data()
    cache = fs.load_data(Path("data/cache/sales.json"))
    saless_path = Path("data/sales")
    fs.clear_terminal()
    print("--- Sales ---\n")

    # get invoice
    while True:
        invoice = sfs.get_invoice(cache, saless_path)
        if invoice:
            break

    # add invoice items
    while True:
        fs.clear_terminal()
        item = None

        # get item
        while True:
            str_or_float = fs.get_str_or_float("Item Name/Serial Number (check-out)", True)
            if not str_or_float:
                return sfs.check_out(cache, invoice)
            item = sfs.get_item(invoice, items, cache, str_or_float)
            if item:
                break

        item_in_invoice = False
        for _item in invoice['items']:
            if _item["serial-numbers"][0] in item["serial-numbers"]:
                item["sold-items"] += _item["sold-items"]
                item["sold-packs"] += _item["sold-packs"]
                item["total-sold-price"] += _item["total-sold-price"]
                invoice['items'].remove(_item)
                invoice['items'].append(item)
                item_in_invoice = True
                break
        if not item_in_invoice:
            invoice['items'].append(item)

        invoice["total"] += item["total-sold-price"]


if __name__ == "__main__":
    while True:
        try:
            sales()
            fs.get_str("(continue)", True)
        except fs.ManzumaException:
            continue
