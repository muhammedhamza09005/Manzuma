from pathlib import Path
from pprint import pprint
from typing import Any

import functions.functions as fs
import functions.users_functions as ufs


class Users:
    def __init__(self):
        # Settings
        self.settings = ufs.UsersSettings()
        self.cache = dict()
        self.secret = dict()
        self.users_path = Path("data/users")
        self.users = list()

    def init_users(self):
        fs.clear_terminal()
        print("Loding users...")
        ufs.merge_users(self)
        self.cache = fs.load_data(Path("data/cache/users.json"))
        self.secret = fs.load_data(Path("data/secret.json"))
        fs.clear_terminal()
        print("--- Users ---\n")

    def main(self) -> dict[str, Any]:
        # init users
        self.init_users()

        # get user
        while True:
            self.user = ufs.get_user(self)
            if self.user:
                break

        self.user_path = Path(f"{self.users_path}/{self.user['username']}.json")
        self.user["user-path"] = str(self.user_path)

        # update user permissions
        ufs.update_user_permissions(self)

        # Save items
        fs.clear_terminal()
        print("Saving items...")
        errors = list()
        if not fs.dump_data(self.cache, Path("data/cache/users.json")):
            errors.append("cache")
        if not fs.dump_data(self.user, self.user_path):
            errors.append("user")
        if errors:
            fs.get_str(self, f"{len(errors)} error(s) found: {fs.desplit(errors)} (continue)", True)

        return self.user


if __name__ == "__main__":
    while True:
        try:
            pprint(Users().main())
            fs.get_str(None, "(continue)", True)
        except fs.ManzumaException:
            continue
