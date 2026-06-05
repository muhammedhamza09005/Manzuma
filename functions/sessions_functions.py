from typing import Any
from pathlib import Path

import functions.functions as fs
import functions.users_functions as ufs
import users as u


def login(self) -> dict[str, Any]:
    loged_in_user = fs.load_data(Path("data/loged_in_user.json"))
    if loged_in_user:
        self.user = loged_in_user
        return loged_in_user
    fs.clear_terminal()
    users = u.Users()
    users.init_users()
    fs.clear_terminal()
    print("--- Login ---\n")
    ufs.merge_users(users)
    if not users.users:
        self.user = users.main()
        fs.dump_data(self.user, Path("data/loged_in_user.json"))
        return self.user
    while True:
        username_name = fs.get_str(self, "Username / Name (new user)", True)
        if not username_name:
            self.user = users.main()
            fs.dump_data(self.user, Path("data/loged_in_user.json"))
            return self.user
        password = fs.get_str_or_float(self, "Password")
        for user in users.users:
            decrypted_password = ufs.decrypt_password(user["password"], users.secret["key"].encode("utf-8"))
            if username_name in [user["username"], user["name"]] and decrypted_password == password:
                self.user = user
                fs.dump_data(self.user, Path("data/loged_in_user.json"))
                return self.user
        print("Username and password do not match!")
        fs.clear_terminal()


def logout() -> None:
    fs.dump_data(dict(), Path("data/loged_in_user.json"))
