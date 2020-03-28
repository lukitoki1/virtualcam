from window import WindowHandler, Config

from PySide2.QtWidgets import (QApplication)
import argparse
import json
import numpy as np


class App:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.app: QApplication = None
        self.window: WindowHandler = None

        self.run()

    def run(self):
        self.prepare_parser()
        self.app = QApplication()
        self.window = WindowHandler(*self.read_config())

        self.window.show()
        self.app.exec_()

    def prepare_parser(self):
        self.parser.add_argument('config_path', metavar='CONF', type=str, nargs=1,
                                 help='A path to the JSON config file.')

    def read_config(self) -> (np.array, Config):
        args = vars(self.parser.parse_args())
        config_path = args['config_path'][0]
        with open(config_path, encoding='utf=8') as config_file:
            config_dict = json.load(config_file)
            return np.array(config_dict['polygons']), Config(config_dict)


app = App()
