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

    def transfer_files(self, target_name: str, shoot_date: str, cut_paste=True) -> None:

        # Copy the full directory tree from source to destination
        extended_destination = os.path.join(self.destination_path, target_name, f'{target_name}_{shoot_date}')
        shutil.copytree(os.path.join(self.source_path), dst=extended_destination)

        # Delete EOSMISC folder
        shutil.rmtree(os.path.join(extended_destination, 'EOSMISC'), ignore_errors=True)

        # Rename destination folders
        for pre, post in self.FOLDER_MAP.items():
            os.rename(src=os.path.join(extended_destination, pre), dst=os.path.join(extended_destination, post))

        # Delete files from source directory
        if cut_paste:
            for folder_name in os.listdir(self.source_path):
                if folder_name == 'EOSMISC':
                    continue
                folder_path = os.path.join(self.source_path, folder_name)
                for file_name in os.listdir(folder_path):
                    img_path = os.path.join(folder_path, file_name)
                    os.remove(img_path)


if __name__ == "__main__":
    fm = FileManager()
    fm.transfer_files(target_name='M42', shoot_date='241218', cut_paste=True)
