from pprint import pprint

import functions.functions as fs


class Save:
    def __init__(self):
        self.data = fs.load_data()
        self.kill_process = True

    # Main function
    def save(self):
        fs.clear_terminal()


def save(data: list[dict]) -> list[dict]:
    temp_dict = None
    while True:
        str_or_float = fs.get_str_or_float('Name / Serial Number')
        fs.clear_terminal()
        if type(str_or_float) is str:
            _data = fs.get_items(data, name=str_or_float)
            if type(_data) is list and len(_data) == 1:
                temp_dict = _data[0]
                serial_number = _data[0]['serial-numbers'][0]
                break
            pprint(_data)
            continue
        else:
            serial_number = int(str_or_float)
            break
    fs.clear_terminal()
    pprint(fs.get_items(data, serial_number))
    is_found = False
    for _dict in data:
        try:
            if temp_dict or serial_number in _dict['serial-numbers']:
                if temp_dict:
                    _dict = temp_dict
                is_found = True
                fs.create_serial_number(data, _dict)
                in_stock = fs.get_str_or_float('Add to In-Stock?', True)
                if in_stock is None:
                    return data
                if type(in_stock) is str and "=" in in_stock:
                    _in_stock = float(in_stock.split("=")[1])
                    _dict['total-purchase-price('] = _dict['purchase-price'] * _in_stock
                    _dict['stock-difference'] = _in_stock - _dict['imported']
                else:
                    _dict['total-purchase-price('] = _dict['purchase-price'] * (in_stock + _dict['in-stock'])
                    _dict['stock-difference'] = (in_stock + _dict['in-stock']) - _dict['imported']
                if not in_stock:
                    _dict['total-purchase-price('] = int()
                    _dict['in-stock'] = int()
                elif type(in_stock) is str and "=" in in_stock:
                    _dict['in-stock'] = float(in_stock.split("=")[1])
                else:
                    _dict['in-stock'] += in_stock
                pprint(_dict)
                return data
        except KeyError as e:
            print('Error', e)
    if not is_found:
        name = fs.get_str('Name')
        imported = fs.get_float('imported')
        in_stock = fs.get_float('In-Stock')
        purchase_price = fs.get_float('Purchase Price')
        new_data = {
            'serial-numbers': [int(serial_number)],
            'imported': imported,
            'in-stock': in_stock,
            'name': name,
            'purchase-price': purchase_price,
            'sell-price': fs.get_float('Sell Price'),
            'total-purchase-price(': purchase_price * imported,
            'stock-difference': in_stock - imported,
        }
        data.append(new_data)
        if not fs.create_serial_number(data, new_data):
            pprint(new_data)
        return data


if __name__ == "__main__":
    while True:
        data = fs.load_data()
        fs.dump_stock_difference(data)
        fs.dump_data(save(data))
