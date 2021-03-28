import json
import logging
import os


class JsonDatabase:

    @staticmethod
    def retrieve_database(json_file: str):
        try:
            with open(f'{os.getcwd()}/database/{json_file}') as database:
                data = json.load(database)
            return data
        except Exception as e:
            logging.error(e)

    @staticmethod
    def update_database(data: dict, json_file: str):
        try:
            with open(f'{os.getcwd()}/database/{json_file}', 'w') as database:
                json.dump(data, database)
            print('update_database')
        except Exception as e:
            logging.error(e)
