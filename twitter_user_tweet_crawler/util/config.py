from pathlib import Path

from yaml import dump, safe_load


class Config:
    proxy: dict | None
    max_threads: int
    user_data_dir: str
    header: dict
    inject_js: str
    save: str
    user: str

    def load(self, setting: dict | str | Path):
        if isinstance(setting, dict):
            self.__dict__.update(setting)
        else:
            with open(setting) as f:
                self.__dict__.update(safe_load(f))

    def save(self):
        with open(work_directory / "config.yaml", 'w') as f:
            dump(self, f)

    def __getitem__(self, item):
        return self.__dict__[item]


work_directory: Path = Path()


def set_work_directory(path: Path):
    global work_directory
    work_directory = path


config = Config()
