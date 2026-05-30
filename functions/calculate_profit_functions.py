import functions.functions as fs


class CalculateProfitSettings(fs.Settings):
    def __init__(self):
        super().__init__()
        self.notes_history = 5
        self.kill_process = True


def notes(self, _input: float, value: float) -> None:
    if self.list:
        if len(self.list) <= 5:
            print("History:")
            for key, pair in self.list:
                print(f"{key} -> {pair:.2f}")
        else:
            print("History (last 5 calculations):")
            for key, pair in self.list[-5:]:
                print(f"{key} -> {pair:.2f}")
        print("\nResult:")
    else:
        print("Result:")
    self.list.append((_input, value))
