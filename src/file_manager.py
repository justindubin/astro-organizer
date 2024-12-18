import os
import time
import yaml
import shutil
import functools
from pathlib import Path
from datetime import timedelta


class MissingInputError(Exception):
    def __init__(self, message, error_code):
        self.message = message
        super().__init__(self.message)
        self.error_code = error_code

    def __str__(self):
        return f"[Errno {self.error_code}] {self.message}"


class FileManager:

    # Create a cfg file if none exists
    CONFIG_PATH = os.path.join(str(Path(__file__).parent.parent), "cfg/config.yaml")
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

    def update_last(self, source_path=None, destination_path=None) -> None:
        if source_path is not None:
            self.config_data['last_paths']['source'] = source_path
        if destination_path is not None:
            self.config_data['last_paths']['destination'] = destination_path
        with open(self.CONFIG_PATH, 'w') as f:
            yaml.dump(self.config_data, f, default_flow_style=False)

    @staticmethod
    def validate_inputs(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            for arg_idx, field_key in enumerate(["target_name", "shoot_date"]):
                if field_key not in kwargs.keys():
                    field_value = args[arg_idx]
                else:
                    field_value = kwargs[field_key]

                if not field_value:
                    field_name = field_key.replace('_', ' ').title()
                    raise MissingInputError(f'Missing required input: {field_name}', 400)

            func(self, *args, **kwargs)
        return wrapper

    @validate_inputs
    def transfer_files(self, target_name: str, shoot_date: str, cut_paste=True, signaler=None) -> None:
        _t0 = time.perf_counter()

        if signaler:
            signaler.progress.emit('*' * 49)
            signaler.progress.emit(f'\nInitiating file transfer session:')
            signaler.progress.emit(f'    * Target:  {target_name}')
            signaler.progress.emit(f'    * Date:  {shoot_date[2:4]}/{shoot_date[4:]}/{shoot_date[:2]}')

        # Copy the full directory tree from source to destination
        extended_destination = os.path.join(self.destination_path, target_name, f'{target_name}_{shoot_date}')
        if signaler:
            signaler.progress.emit(f'\nCopying directory tree to destination ...')
        t0 = time.perf_counter()
        shutil.copytree(os.path.join(self.source_path), dst=extended_destination)
        t1 = time.perf_counter()
        if signaler:
            signaler.progress.emit(f'Completed transfer in {timedelta(seconds=t1-t0)}')

        # Delete EOSMISC folder
        shutil.rmtree(os.path.join(extended_destination, 'EOSMISC'), ignore_errors=True)

        # Rename destination folders
        if signaler:
            signaler.progress.emit(f'\nRenaming folders for Siril compliance ...')
        t0 = time.perf_counter()
        for pre, post in self.FOLDER_MAP.items():
            os.rename(src=os.path.join(extended_destination, pre), dst=os.path.join(extended_destination, post))
            if signaler:
                signaler.progress.emit(f'    * {pre} --> {post}')
        t1 = time.perf_counter()
        if signaler:
            signaler.progress.emit(f'Completed renaming in {timedelta(seconds=t1-t0)}')

        # Delete files from source directory
        if cut_paste:
            if signaler:
                signaler.progress.emit(f'\nRemoving files from source directory ...')
            t0 = time.perf_counter()
            for folder_name in os.listdir(self.source_path):
                if folder_name == 'EOSMISC':
                    continue
                folder_path = os.path.join(self.source_path, folder_name)
                for file_name in os.listdir(folder_path):
                    img_path = os.path.join(folder_path, file_name)
                    try:
                        os.remove(img_path)
                    except FileNotFoundError:
                        pass  # Workaround for MacOS
            t1 = time.perf_counter()
            if signaler:
                signaler.progress.emit(f'Cleaned source directory in {timedelta(seconds=t1 - t0)}')

        _t1 = time.perf_counter()
        if signaler:
            signaler.progress.emit('')
            signaler.progress.emit(f' Process completed in {timedelta(seconds=_t1-_t0)} '.center(50, '*'))


if __name__ == "__main__":
    fm = FileManager()
    fm.transfer_files(target_name='M42', shoot_date='241218', cut_paste=True)
