from pathlib import Path
from typing import Any

import functions.functions as fs
import functions.profits_functions as pfs
import functions.sessions_functions as sefs


class Profits:
    def __init__(self):
        # Settings
        self.settings = pfs.ProfitsSettings()
        self.items = list()
        self.cache = dict()
        self.sales_path = Path("data/sales")
        self.invoices = list()

    def init_profits(self):
        fs.clear_terminal()
        print("Loding profits...")
        fs.merge_invoices(self, self.sales_path)
        sefs.login(self)
        fs.clear_terminal()
        print("--- Profits ---\n")

    def main(self) -> None:
        # init profits
        self.init_profits()

        profit = float()
        for invoice in self.invoices:
            profit += invoice["total-profit"]

        print(f"Profit: {profit}")


if __name__ == "__main__":
    while True:
        try:
            Profits().main()
            fs.get_str(None, "(continue)", True)
        except fs.ManzumaException:
            continue
