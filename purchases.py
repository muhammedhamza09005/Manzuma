from pathlib import Path
from pprint import pprint

import functions as fs


def purchases() -> dict | None:
    # init purchases
    fs.clear_terminal()
    print(f"Loding purchases...")
    items = fs.load_data()
    cache = fs.load_data(Path("data/cache.json"))
    purchases_path = Path("data/purchases")
    fs.clear_terminal()
    print(f"--- Purchases ---\n")

    # get invoice
    invoice = fs.get_invoice(cache, purchases_path)
    if not invoice:
        print('purchases error: not invoice')
        return

    # add invoice items
    while True:
        if invoice['items']:
            fs.clear_terminal()
            if not fs.get_str_or_float("Add a new item? (no)", True):
                break

        # get item
        while True:
            item, status = fs.get_item(items, cache)
            if item:
                break

        if status == "get":
            item_in_invoice = False
            for _item in invoice['items']:
                if _item["serial-numbers"][0] in item["serial-numbers"]:
                    item = fs.add_to_item(items, _item)
                    invoice['items'].remove(_item)
                    invoice['items'].append(item)
                    item_in_invoice = True
                    break
            if not item_in_invoice:
                item = fs.update_item(items, item)
                invoice['items'].append(item)
        else:
            invoice['items'].append(item)

    # Save items
    fs.clear_terminal()
    print(f"Saving items...")
    saved_all = True
    if fs.dump_data(cache, Path("data/cache.json")):
        print("cache -> OK")
    else:
        saved_all = False
    if fs.dump_data(invoice, f"{purchases_path}/{invoice['invoice-number']}-{invoice['supplier']}.json"):
        print("invoice -> OK")
    else:
        saved_all = False
    items = fs.merge_purchases_items()
    if fs.dump_data(items):
        print("items -> OK")
    else:
        saved_all = False
    if fs.dump_stock_difference(items):
        print("stock_difference -> OK")
    else:
        saved_all = False
    if saved_all:
        fs.clear_terminal()

    return invoice


if __name__ == "__main__":
    while True:
        invoice = purchases()
        if invoice:
            pprint(invoice)
