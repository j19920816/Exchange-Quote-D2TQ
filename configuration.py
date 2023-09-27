import configparser
import os


class Config(object):
    def __init__(self, file_name: str) -> None:
        self.__config: configparser.ConfigParser = configparser.ConfigParser()
        self.__file_name: str = file_name
        self.subscribe_symbols: list

    def load_config(self: str):
        isExists = os.path.isfile(self.__file_name)
        if not isExists:
            f = open(self.__file_name)
            f.close()
            return

        self.__config.read(self.__file_name)
        sections = self.__config.sections()
        if len(sections) == 0:
            return

        if self.__config.has_section("Subscribe"):
            self.subscribe_symbols = self.__config["Subscribe"]["symbols"].split(",")

'''
    def save_config(self):
        self.__config["BitoPro"] = {"Account": self.account, "ApiKey": self.api_key,
                                    "Secret": self.secret_key}
        self.__config["Line"] = {"LineToken": self.line_token}

        with open(self.__file_name, 'w') as configfile:
            self.__config.write(configfile)
'''
