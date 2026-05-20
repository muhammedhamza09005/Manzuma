from datetime import date
from pathlib import Path
from pprint import pprint

import functions as fs
from calculate_profit import main as profit


def main():
    fs.clear_terminal()
    data = fs.load_data()
    supplier = str(fs.get_str("Supplier"))
    folder_path = Path("json/purchases")
    invoice_number = sum(1 for f in folder_path.iterdir() if f.is_file()) + 1
    today = date.today().isoformat()  # convert to ISO string
    _date = fs.validate_date(fs.get_str(f"Date ({today})", True))
    invoice = {
        "supplier": supplier,
        "date": str(_date or today),
        "invoice-number": invoice_number,
        "supplier-invoice-number": int(fs.get_float("Supplier Invoice Number")),
        "items": list(),
    }
    # items
    while True:
        if invoice['items']:
            fs.clear_terminal()
            if not fs.get_str_or_float("Add a new item? (no)", True):
                break
        name = fs.get_str('Item Name')
        imported = fs.get_float('imported')
        in_stock = fs.get_float('In-Stock')
        purchase_price = fs.get_float('Purchase Price')
        profit_sell_price = profit(10, 0.25, purchase_price)
        sell_price = fs.get_float(f'Sell Price ({purchase_price} -> {profit_sell_price})', True)
        item = {
            'serial-numbers': [int(fs.get_float("Serial Number"))],
            'imported': imported,
            'in-stock': in_stock,
            'name': name,
            'purchase-price': purchase_price,
            'sell-price': sell_price or profit_sell_price,
            'total-price': purchase_price * imported,
            'stock-difference': in_stock - imported,
        }
        data.append(item)
        fs.add_new_serial_number(data, item)
        invoice['items'].append(item)
    fs.dump_stock_difference(data)
    fs.clear_terminal()
    pprint(invoice)
    fs.dump_data(invoice, f"{folder_path}/{invoice_number}.json")
    fs.dump_data(data)


if __name__ == "__main__":
    main()
