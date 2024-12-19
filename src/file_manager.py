from datetime import datetime, timedelta
import functools
import os
from pathlib import Path
import shutil
import time

from dotenv import load_dotenv, find_dotenv, set_key

from src.custom_error import CustomError


class FileManager:

    ENV_FILE_PATH = os.path.join(Path(__file__).parent.parent, '.env')
    FOLDER_MAP = {
        '100_BIAS': 'biases',
        '101_DARK': 'darks',
        '102_FLAT': 'flats',
        '103_LITE': 'lights',
    }

    def __init__(self):
        self._source_path = None
        self._destination_path = None
        if not os.path.exists(self.ENV_FILE_PATH):
            with open(self.ENV_FILE_PATH, 'w') as f:
                f.write("SOURCE_DIR=''\nDESTINATION_DIR=''")
        self.dotenv_path = find_dotenv()
        load_dotenv(self.dotenv_path)
        self.recall_paths()

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

    def recall_paths(self) -> None:
        self.source_path = os.getenv("SOURCE_DIR")
        self.destination_path = os.getenv("DESTINATION_DIR")

    def update_paths(self, source_path=None, destination_path=None) -> None:
        if source_path is not None:
            os.environ["SOURCE_DIR"] = source_path
            set_key(self.dotenv_path, "SOURCE_DIR", os.environ["SOURCE_DIR"])
        if destination_path is not None:
            os.environ["DESTINATION_DIR"] = destination_path
            set_key(self.dotenv_path, "DESTINATION_DIR", os.environ["DESTINATION_DIR"])

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
                    raise CustomError(f'Missing required input: {field_name}', 400)

            func(self, *args, **kwargs)
        return wrapper

    @validate_inputs
    def transfer_files(self, target_name: str, shoot_date: str, cut_paste=True, signaler=None) -> None:
        _t0 = time.perf_counter()

        # Convert to datetime
        extended_destination = os.path.join(self.destination_path, target_name, f'{target_name}_{shoot_date}')
        try:
            shoot_date = datetime.strptime(shoot_date, "%y%m%d")
        except ValueError:
            raise CustomError(f'Invalid input: Unable to convert string "{shoot_date}"to datetime object\n\nPlease ensure input string conforms to the YYMMDD convention', 401)

        if signaler:
            signaler.progress.emit('*' * 49)
            signaler.progress.emit(f'\nInitiating file transfer session:')
            signaler.progress.emit(f'    * Target:  {target_name}')
            signaler.progress.emit(f'    * Date:  {shoot_date:%B %d, %Y}')

        # Copy the full directory tree from source to destination
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
