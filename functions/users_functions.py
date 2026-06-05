import datetime
import os
from pathlib import Path
from pprint import pprint
from typing import Any

from cryptography.fernet import Fernet

import functions.functions as fs


def merge_users(self):
    for user_path in self.users_path.iterdir():
        if user_path.is_file():
            self.users.append(fs.load_data(user_path))


class UsersSettings(fs.Settings):
    def __init__(self):
        super().__init__()


def encrypt_password(password: str, key: bytes) -> str:
    """
    * Encrypts a password using a Fernet key.
    """
    return Fernet(key).encrypt(password.encode()).decode("utf-8")


def decrypt_password(encrypted_password: bytes, key: bytes) -> str:
    """
    * Decrypts an encrypted password back to a string.
    """
    return Fernet(key).decrypt(encrypted_password).decode("utf-8")


def create_user(self) -> dict[str, Any]:
    user_dict = dict()
    while True:
        name = fs.get_str(self, "Name")
        name_already_exists = False
        for user in self.users:
            if fs.sanitized_and_desplited(user["name"]) == fs.sanitized_and_desplited(name):
                print(f"Name ({name}) already exists!")
                name_already_exists = True
                break
        username = f"{self.cache['last-user-number'] + 1}-{fs.clean_file_name(name)}"
        if not name_already_exists:
            user_dict["name"] = name
            user_dict["username"] = username
            break
    while True:
        password1 = fs.get_str_or_float(self, "New Password")
        password2 = fs.get_str_or_float(self, "New Password Again")
        if password1 != password2:
            print("Passwords do not match!")
            continue
        if len(password1) < 8:
            print("Password is too short! Min: 8.")
            continue
        user_dict["password"] = encrypt_password(password1, self.secret["key"].encode("utf-8"))
        break
    self.cache["last-user-number"] += 1
    user_dict["user-number"] = self.cache["last-user-number"]
    self.cache["user-numbers"].append(self.cache["last-user-number"])
    user_dict["date"] = datetime.date.today().isoformat()  # convert to ISO string
    user_dict.update({"user-path": str(), "permissions": dict()})
    return user_dict


def get_user(self) -> dict | None:
    if not self.cache["user-numbers"]:
        return create_user(self)
    user_number = fs.get_float(self, "User Number (new user)", True)
    if not user_number:
        return create_user(self)
    user_number = int(user_number)
    is_delete = False
    if user_number < 0:
        user_number *= -1
        is_delete = True
    users = [user for user in self.users if user_number == user["user-number"]]
    if len(users) == 1:
        if is_delete and not fs.get_str(self, f"Are you sure you want to DELETE user user: {user_number}? (Yes)", True):
            return delete_user(self, Path(users[0]["user-path"]), user_number)
        return users[0]
    pprint([(user["user-number"], user["username"], user["name"]) for user in (users or self.users)])


def update_user_permissions(self):
    if self.user["permissions"] and not self.user["permissions"]["super-user"]:
        print(f"You do not have a permisstion to update your permissions!")
        return

    permissions = dict()

    """ Superuser """
    super_user = fs.get_str_or_float(self, "Super User? (no)", True)
    if super_user:
        permissions["super-user"] = True
        self.user["permissions"].update(permissions)
        return
    permissions["super-user"] = False

    """ Purchases """
    if bool(fs.get_str_or_float(self, "All Purchase Permissions? (no)", True)):
        permissions["create-supplier"] = True
        permissions["create-purchase-invoice"] = True
        permissions["delete-purchase-invoice"] = True
        permissions["create-purchase-item"] = True
        permissions["update-purchase-item"] = True
        permissions["delete-purchase-item"] = True
    else:
        # supplier permissions
        permissions["create-supplier"] = bool(fs.get_str_or_float(self, "Create Supplier? (no)", True))
        # purchase invoice permissions
        permissions["create-purchase-invoice"] = bool(fs.get_str_or_float(self, "Create Purchase Invoice? (no)", True))
        permissions["delete-purchase-invoice"] = bool(fs.get_str_or_float(self, "Delete Purchase Invoice? (no)", True))
        # purchase items permissions
        permissions["create-purchase-item"] = bool(fs.get_str_or_float(self, "Create Purchase Item? (no)", True))
        permissions["update-purchase-item"] = bool(fs.get_str_or_float(self, "Update Purchase Item? (no)", True))
        permissions["delete-purchase-item"] = bool(fs.get_str_or_float(self, "Delete Purchase Item? (no)", True))

    """ Saless """
    if bool(fs.get_str_or_float(self, "All Sales Permissions? (no)", True)):
        permissions["create-customer"] = True
        permissions["create-sales-invoice"] = True
        permissions["delete-sales-invoice"] = True
        permissions["create-sales-item"] = True
        permissions["update-sales-item"] = True
        permissions["delete-sales-item"] = True
    else:
        # customer permissions
        permissions["create-customer"] = bool(fs.get_str_or_float(self, "Create Customer? (no)", True))
        # sales invoice permissions
        permissions["create-sales-invoice"] = bool(fs.get_str_or_float(self, "Create Sales Invoice? (no)", True))
        permissions["delete-sales-invoice"] = bool(fs.get_str_or_float(self, "Delete Sales Invoice? (no)", True))
        # sales items permissions
        permissions["create-sales-item"] = bool(fs.get_str_or_float(self, "Create Sales Item? (no)", True))
        permissions["update-sales-item"] = bool(fs.get_str_or_float(self, "Update Sales Item? (no)", True))
        permissions["delete-sales-item"] = bool(fs.get_str_or_float(self, "Delete Sales Item? (no)", True))

    self.user["permissions"].update(permissions)


def delete_user(self, user_path: Path, user_number: int) -> None:
    if os.path.exists(user_path) and user_path.is_file():
        os.remove(user_path)
    self.cache["user-numbers"].remove(user_number)
    fs.dump_data(dict(), Path("data/loged_in_user.json"))
    fs.dump_data(self.cache, Path("data/cache/users.json"))
    fs.check_quit(self, "00")
