class UpdateGameConfig:
    def __init__(self, data: dict) -> None:
        self.data = data

    def update(self) -> None:
        with open(self.data["Game_Info"]["config_path"], "r") as f:
            lines = f.readlines()
            data = []
            for i in lines:
                key = i.split('=')[0]
                if key in self.data["Game_Info"]["change_content"]:
                    i = key + '=' + self.data["Game_Info"]["change_content"][key] + '\n'
                data.append(i)
        with open(self.data["Game_Info"]["config_path"], "w") as f:
            for i in data:
                f.writelines(i)
