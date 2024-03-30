class ChangeConfig:
    def __init__(self, data:dict) -> None:
        self.data = data

    def change(self) -> None:
        with open(self.data["game_config_path"], "r") as f:
            lines = f.readlines()
            data = []
            for i in lines:
                key = i.split('=')[0]
                if key in self.data["game_change_content"]:
                    i = key + '=' + self.data["game_change_content"][key] + '\n'
                data.append(i)
        with open(self.data["game_config_path"], "w") as f:
            for i in data:
                f.writelines(i)
