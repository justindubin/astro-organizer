import os
import yaml
import shutil


class FileManager:

    # Create a config file if none exists
    CONFIG_PATH = "../config/config.yaml"
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump({'last_paths': {'source': None, 'destination': None}}, f, default_flow_style=False)

    FOLDER_MAP = {
        '100_BIAS': 'biases',
        '101_DARK': 'darks',
        '102_FLAT': 'flats',
        '103_LITE': 'lights',
    }

    def __init__(self):
        self._config_data = None
        self._source_path = None
        self._destination_path = None
        self.target_name = None
        self.shoot_date = None
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

    def transfer_files(self, target_name: str, shoot_date: str, copy=False) -> None:
        extended_destination = os.path.join(self.destination_path, target_name, f'{target_name}_{shoot_date}')
        shutil.copytree(os.path.join(self.source_path), dst=extended_destination)

        # ToDo: Delete EOSMISC
        shutil.rmtree(os.path.join(extended_destination, 'EOSMISC'))
        # ToDo: Rename destination folders
        for pre, post in self.FOLDER_MAP.items():
            os.rename(src=os.path.join(extended_destination, pre), dst=os.path.join(extended_destination, post))

        # ToDo: Erase SD card if copy == False


if __name__ == "__main__":
    fm = FileManager()
    fm.transfer_files(target_name='M42', shoot_date='241216')
    # print(fm.source_path, fm.destination_path)
    # fm.update_last("/Volumes/CANON_256GB/DCIM", "/Volumes/JDUBIN_EXT/Astrophotography/Projects")
    # fm.recall_last()
    # print(fm.source_path, fm.destination_path)
