import os
import yaml
from pathlib import Path
from datetime import datetime


class FileManager:

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
    def config_data(self, config_data: dict):
        self._config_data = config_data

    @property
    def source_path(self) -> str:
        return self._source_path

    @source_path.setter
    def source_path(self, source_path: str):
        self._source_path = source_path

    @property
    def destination_path(self) -> str:
        return self._destination_path

    @destination_path.setter
    def destination_path(self, destination_path: str):
        self._destination_path = destination_path

    def recall_last(self):
        with open("../config/config.yaml", 'r') as f:
            self.config_data = yaml.load(f, Loader=yaml.FullLoader)
        try:
            self.source_path = self.config_data['last_paths']['source']
        except TypeError:
            self.source_path = None
        try:
            self.destination_path = self.config_data['last_paths']['destination']
        except TypeError:
            self.destination_path = None

    def update_last(self):
        pass


if __name__ == "__main__":
    fm = FileManager()
    sd = os.listdir(fm.source_path)
    dd = os.listdir(fm.destination_path)
