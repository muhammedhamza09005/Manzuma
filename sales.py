import datetime
from pathlib import Path
from typing import Any

import functions.functions as fs
import functions.purchase_functions as pfs
import functions.sales_functions as sfs


class Sales:
    def __init__(self):
        # Settings
        self.settings = sfs.SalesSettings()
        self.items = list()
        self.cache = dict()
        self.purchases_path = Path("data/purchases")
        self.sales_path = Path("data/sales")
        self.invoice = dict()

    def init_sales(self):
        fs.clear_terminal()
        print("Loding sales...")
        self.purchased_items = pfs.merge_items(self)
        self.sold_items = sfs.merge_items(self)
        self.cache = fs.load_data(Path("data/cache/sales.json"))
        self.invoice_path = Path()
        fs.clear_terminal()
        print("--- Sales ---\n")

    def main(self) -> dict[str, Any]:
        # init sales
        self.init_sales()

        # get invoice
        while True:
            self.invoice = sfs.get_invoice(self)
            if self.invoice:
                break

        today = datetime.date.today().isoformat()  # convert to ISO string
        Path(f"{self.sales_path}/{today}").mkdir(exist_ok=True)
        self.invoice_path = Path(
            f"{self.sales_path}/{today}/{self.invoice['invoice-number']}-"
            f"{fs.clean_file_name(self.invoice['customer']['customer-name'])}.json"
        )

        # add invoice items
        while True:
            fs.clear_terminal()
            item = None

            # get item
            while True:
                message = " (check-out)" if self.invoice["items"] else str()
                str_or_float = fs.get_str_or_float(
                    f"Item Name/Serial Number{message}", True if self.invoice["items"] else False
                )
                if not str_or_float:
                    return sfs.check_out(self)
                item = sfs.get_item(self, str_or_float)
                if item:
                    break

            item_in_invoice = False
            for _item in self.invoice['items']:
                if _item["serial-numbers"][0] in item["serial-numbers"]:
                    item["sold-items"] += _item["sold-items"]
                    item["sold-packs"] += _item["sold-packs"]
                    item["total-sold-price"] += _item["total-sold-price"]
                    self.invoice['items'].remove(_item)
                    self.invoice['items'].append(item)
                    item_in_invoice = True
                    break
            if not item_in_invoice:
                self.invoice['items'].append(item)

            self.invoice["total"] += item["total-sold-price"]


if __name__ == "__main__":
    while True:
        try:
            Sales().main()
            fs.get_str("(continue)", True)
        except fs.ManzumaException:
            continue
