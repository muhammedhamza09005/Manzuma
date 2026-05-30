from pathlib import Path
from pprint import pprint
from typing import Any

import functions.functions as fs
import functions.purchase_functions as pfs
from calculate_profit import CalculateProfit


class Purchases:
    def __init__(self):
        # Settings
        self.settings = pfs.PurchasesSettings()
        self.items = list()
        self.cache = dict()
        self.purchases_path = Path("data/purchases")
        self.invoice = dict()

    def init_purchases(self):
        fs.clear_terminal()
        print("Loding purchases...")
        self.items = pfs.merge_items(self)
        self.cache = fs.load_data(Path("data/cache/purchases.json"))
        self.calculate_profit = CalculateProfit().main
        fs.clear_terminal()
        print("--- Purchases ---\n")

    def main(self) -> dict[str, Any]:
        # init purchases
        self.init_purchases()

        # get invoice
        while True:
            self.invoice = pfs.get_invoice(self)
            if self.invoice:
                break

        self.invoice_path = Path(
            f"{self.purchases_path}/{self.invoice['invoice-number']}-"
            f"{self.invoice['supplier']['shorted-supplier-name']}.json"
        )

        # add invoice items
        while True:
            if self.invoice['items']:
                fs.clear_terminal()
                if not fs.get_str_or_float("Add a new item? (no)", True):
                    break

            # get item
            while True:
                item, status = pfs.get_item(self)
                if item:
                    break

            if status == "get":
                item_in_invoice = False
                for _item in self.invoice['items']:
                    if _item["serial-numbers"][0] in item["serial-numbers"]:
                        item = pfs.add_to_item(self, _item)
                        self.invoice['items'].remove(_item)
                        self.invoice['items'].append(item)
                        item_in_invoice = True
                        break
                if not item_in_invoice:
                    item = pfs.update_item(self.items, item)
                    self.invoice['items'].append(item)
            else:
                self.invoice['items'].append(item)

        # Save items
        fs.clear_terminal()
        print("Saving items...")
        errors = list()
        if not fs.dump_data(self.cache, Path("data/cache/purchases.json")):
            errors.append("cache")
        if not fs.dump_data(self.invoice, self.invoice_path):
            errors.append("invoice")
        if not pfs.dump_stock_difference(self):
            errors.append("stock_difference")
        if errors:
            fs.get_str(f"{len(errors)} error(s) found: {fs.desplit(errors)} (continue)", True)

        return self.invoice


if __name__ == "__main__":
    while True:
        try:
            pprint(Purchases().main())
            fs.get_str("(continue)", True)
        except fs.ManzumaException:
            continue
