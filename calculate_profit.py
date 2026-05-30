import functions.calculate_profit_functions as cfs
import functions.functions as fs


class CalculateProfit:
    def __init__(self):
        # Settings
        self.settings = cfs.CalculateProfitSettings()
        self.list = list()

    # Main function
    def main(self, purchase_price: float = float()) -> float | None:
        if not purchase_price:
            fs.clear_terminal()
        while True:
            if not purchase_price:
                _input = fs.get_float("Price")
                fs.clear_terminal()
            else:
                _input = purchase_price
            if _input:
                value = fs.normalize_price(self, _input + (_input / self.settings.profit))
                if purchase_price:
                    return value
                cfs.notes(self, _input, value)
                print(f"{_input} -> {value:.2f}")


if __name__ == "__main__":
    CalculateProfit().main()
