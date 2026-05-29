from pathlib import Path
from pprint import pprint
from typing import Any

import functions.functions as fs
import functions.purchase_functions as pfs


def purchases() -> dict[str, Any]:
    # init purchases
    fs.clear_terminal()
    print("Loding purchases...")
    items = pfs.merge_items()
    cache = fs.load_data(Path("data/cache/purchases.json"))
    purchases_path = Path("data/purchases")
    fs.clear_terminal()
    print("--- Purchases ---\n")

    # get invoice
    while True:
        invoice = pfs.get_invoice(cache, purchases_path)
        if invoice:
            break

    # add invoice items
    while True:
        if invoice['items']:
            fs.clear_terminal()
            if not fs.get_str_or_float("Add a new item? (no)", True):
                break

        # get item
        while True:
            item, status = pfs.get_item(invoice, items, cache)
            if item:
                break

        if status == "get":
            item_in_invoice = False
            for _item in invoice['items']:
                if _item["serial-numbers"][0] in item["serial-numbers"]:
                    item = pfs.add_to_item(items, _item)
                    invoice['items'].remove(_item)
                    invoice['items'].append(item)
                    item_in_invoice = True
                    break
            if not item_in_invoice:
                item = pfs.update_item(items, item)
                invoice['items'].append(item)
        else:
            invoice['items'].append(item)

    # Save items
    fs.clear_terminal()
    print("Saving items...")
    errors = list()
    if not fs.dump_data(cache, Path("data/cache/purchases.json")):
        errors.append("cache")
    invoice_path = f"{purchases_path}/{invoice['invoice-number']}-{invoice['supplier']['shorted-supplier-name']}.json"
    if not fs.dump_data(invoice, invoice_path):
        errors.append("invoice")
    if not pfs.dump_stock_difference(items):
        errors.append("stock_difference")
    if errors:
        fs.get_str(f"{len(errors)} error(s) found: {fs.desplit(errors)} (continue)", True)

    return invoice


if __name__ == "__main__":
    while True:
        try:
            pprint(purchases())
            fs.get_str("(continue)", True)
        except fs.ManzumaException:
            continue
