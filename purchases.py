from pathlib import Path
from pprint import pprint

import functions as fs


def purchases():
    data = fs.load_data()
    cache = fs.load_data(Path("data/cache.json"))
    fs.dump_stock_difference(data)
    fs.clear_terminal()
    supplier_invoice_number = int(fs.get_float("Supplier Invoice Number"))
    purchases_path = Path("data/purchases")
    if supplier_invoice_number in cache["supplier-invoice-numbers"]:
        invoice = None
        for invoice_path in purchases_path.iterdir():
            if invoice_path.is_file():
                _invoice = fs.load_data(invoice_path)
                if supplier_invoice_number == _invoice["supplier-invoice-number"]:
                    invoice = _invoice
                    break
    else:
        invoice = fs.add_new_invoice(cache, supplier_invoice_number)
    if not invoice:
        return
    # items
    while True:
        if invoice['items']:
            fs.clear_terminal()
            if not fs.get_str_or_float("Add a new item? (no)", True):
                break
        serial_number = int(fs.get_float("Serial Number (*)", True) or int())
        if not serial_number:
            serial_number = cache["last-barcode-number"] + 1
            cache["last-barcode-number"] += 1
            fs.dump_data(cache, Path("data/cache.json"))
        items = fs.get_data(data, serial_number)
        if items:
            item = fs.update_item(data, items[0])
        else:
            item = fs.add_new_item(data, serial_number)
        invoice['items'].append(item)
    fs.clear_terminal()
    fs.dump_stock_difference(data)
    pprint(invoice)
    invoice_path = f"{purchases_path}/{invoice['invoice-number']}-{invoice['supplier']}.json"
    fs.dump_data(invoice, invoice_path)
    fs.dump_data(data)


if __name__ == "__main__":
    purchases()
