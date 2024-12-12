import os
import yaml
from datetime import datetime


class FileManager:

    # Create a config file if none exists
    CONFIG_PATH = "../config/config.yaml"
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump({'last_paths': {'source': None, 'destination': None}}, f, default_flow_style=False)

    def __init__(self):
        self._config_data = None
        self._source_path = None
        self._destination_path = None
        self._target_name = None
        self._shoot_date = datetime.now()
        self.recall_last()

    @property
    def config_data(self) -> dict:
        return self._config_data

    @config_data.setter
    def config_data(self, config_data: dict) -> None:
        self._config_data = config_data

    @property
    def source_path(self) -> str:
        return self._source_path

    @source_path.setter
    def source_path(self, source_path: str) -> None:
        self._source_path = source_path

    @property
    def destination_path(self) -> str:
        return self._destination_path

    @destination_path.setter
    def destination_path(self, destination_path: str) -> None:
        self._destination_path = destination_path

    def recall_last(self) -> None:
        with open(self.CONFIG_PATH, 'r') as f:
            self.config_data = yaml.load(f, Loader=yaml.FullLoader)
        try:
            self.source_path = self.config_data['last_paths']['source']
        except TypeError:
            self.source_path = None
        try:
            self.destination_path = self.config_data['last_paths']['destination']
        except TypeError:
            self.destination_path = None

    def update_last(self, source_path: str, destination_path: str) -> None:
        self.config_data['last_paths']['source'] = source_path
        self.config_data['last_paths']['destination'] = destination_path
        with open(self.CONFIG_PATH, 'w') as f:
            yaml.dump(self.config_data, f, default_flow_style=False)


if __name__ == "__main__":
    fm = FileManager()
    # print(fm.source_path, fm.destination_path)
    # fm.update_last("/Volumes/CANON_256GB/DCIM", "/Volumes/JDUBIN_EXT/Astrophotography/Projects")
    # fm.recall_last()
    # print(fm.source_path, fm.destination_path)
