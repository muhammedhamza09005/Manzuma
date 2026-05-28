import functions.functions as fs


class CalculateProfit:
    def __init__(
        self,
        profit: int = int(),
        divide: float = float(),
        notes_history: int = int(),
        kill_process: bool = None,
    ):
        # Settings
        self.profit = profit or 10
        self.divide = divide or 0.25  # divide must be greater than 0
        self.notes_history = notes_history or 5
        self.kill_process = kill_process if kill_process is not None else True


# Main function
def calculate_profit(profit: int, devide: float, purchase_price: float = float()) -> float | None:
    if not purchase_price:
        fs.clear_terminal()
    while True:
        if not purchase_price:
            _input = fs.get_float("Price")
            fs.clear_terminal()
        else:
            _input = purchase_price
        if _input:
            value = fs.normalize_price(_input + (_input / profit), devide)
            if purchase_price:
                return value
            fs.notes(_input, value)
            print(f"{_input} -> {value:.2f}")


if __name__ == "__main__":
    calculate_profit(10, 0.25)
