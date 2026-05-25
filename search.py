from pprint import pprint

import functions as fs


def search() -> list[dict]:
    while True:
        data = fs.load_data()
        str_or_float = fs.get_str_or_float('Name / Serial Number')
        fs.clear_terminal()
        if type(str_or_float) is str:
            _data = fs.get_items(data, name=str_or_float)
            pprint(_data)
        else:
            pprint(fs.get_items(data, str_or_float))


if __name__ == "__main__":
    fs.clear_terminal()
    while True:
        search()
