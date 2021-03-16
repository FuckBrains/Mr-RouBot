# -*- coding: utf-8 -*-
"""
Classe de connection à Oracle
"""
import logging

import cx_Oracle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from application.config.config import Config


class OracleDataBase:

    def __init__(self, mode=None):
        self._mode = mode
        if self._mode == 'pool':
            self.db_pool = cx_Oracle.SessionPool(Config.get_secret('ORA_USERNAME'), Config.get_secret('ORA_PASSWORD'),
                                                 Config.get_secret('CONNECTION_STRING'),
                                                 encoding="UTF-8", nencoding="UTF-8",
                                                 # Pour que les accents soient bien gérés
                                                 min=0, max=20, increment=1)

    def cx_connection(self):
        """
        Méthode permettant la récupération d'une connexion dsn
        Returns
        -------
        Connection
            Objet connection cx_Oracle ouvert vers la BDD
        """
        database_connection = None
        try:
            if self._mode == 'pool':
                database_connection = self.db_pool.acquire()
            else:
                dsn_tns = cx_Oracle.makedsn(Config.get_secret('ORA_SERVER'), Config.get_secret('ORA_PORT'),
                                            Config.get_secret('ORA_SID'))
                database_connection = cx_Oracle.connect(user=Config.get_secret('ORA_USERNAME'),
                                                        password=Config.get_secret('ORA_PASSWORD'),
                                                        dsn=dsn_tns, encoding="UTF-8", nencoding="UTF-8")
        except Exception as ex_conn:
            logging.exception(f' Erreur lors de la connection avec Oracle : {ex_conn}')
        except cx_Oracle.DatabaseError as ora_error:
            logging.exception(f'cx_oracle error: {ora_error}')
        return database_connection

    @staticmethod
    def alchemy_connection():
        """
        Méthode permettant la récupération d'une connection alchemy
        Returns
        -------
        Sql alchemy session
            Objet qui permet l'utilisation de l'ORM
        Sql alchemy engine
            Objet qui ouvre la connexion vers la BDD
        """
        database_connection = None
        try:
            ora_engine = create_engine(
                f"oracle://{Config.get_secret('ORA_USERNAME')}:{Config.get_secret('ORA_PASSWORD')}"
                f"@{Config.get_secret('ORA_SERVER')}/{Config.get_secret('ORA_SID')}", pool_size=20,
                pool_pre_ping=True, max_identifier_length=128)

            alchemy_session = sessionmaker(bind=ora_engine)
            alchemy_sess = alchemy_session()
            database_connection = alchemy_sess.connection().connection
        except Exception as ex_alch:
            logging.exception(f' Erreur lors de la connection avec Oracle : {ex_alch}')
        return database_connection

    def release_pool_connection(self, conn):
        """
        Permet de relâcher une connexion lorsqu'elle n'est plus utilisée

        Parameters
        ----------
        conn: sqlalchemy.orm.session.Session
            Connexion récupérée précédemment via la méthode connection() qui doit être relâchée
        """

        try:
            self.db_pool.release(conn)
            # conn.close()
            logging.info(f" Release OK")
        except Exception as ex_release:
            logging.exception(f' Erreur lors du release : {ex_release}')

    @staticmethod
    def build_insert_query(table_name, dataframe, update=False):
        """
        Crée la requette pour inserer dans une table en utilisant la methode executemany
        /!!!(Il faut obligatoirement que les colonnes du dataframe, match les colonnes de la table)
        Parameters
        ----------
        table_name: Nom de la table vers laquelle inserer
        dataframe: Le dataframe à inserer
        update: Si on update (utiliser la fonction decoratrice update_on_duplicate)

        Returns
        -------
        String: la query à mettre en paramètre dans le executemany
        """
        indexes = []
        query = ''
        try:
            result_columns = tuple(dataframe.columns.tolist())
            for index in range(len(result_columns)):
                indexes.append(f':{index + 1}')
            indexes_tuple = tuple(indexes)
            if not update:
                query = f"""INSERT INTO {table_name} {result_columns} VALUES {indexes_tuple}""".replace("'", "")
            else:
                return result_columns, indexes_tuple
        except Exception as ex_build:
            logging.info(f" Probleme à la création de la query pour executemany : {ex_build}", exc_info=True)
        return query

    def build_insert_update_on_duplicate(self, table_name, dataframe, merge_id, primary_key, sequence_name, seq_func):
        """
        Crée la requette pour inserer ou update en fonction d'un id dans une table
        /!!!(Il faut obligatoirement que les colonnes du dataframe, match les colonnes de la table)
        Parameters
        ----------
        table_name: Nom de la table vers laquelle inserer ou update
        dataframe: Le dataframe à inserer
        merge_id: liste des id unique avec lesquels on fait le merge (si un id mettre une liste d'un element)
        primary_key: la clé primaire de la table
        sequence_name: la sequence a utiliser pour générer la valeur de la clé primaire
        seq_func: la fonction de la sequence (exemple "nextval")

        Returns
        -------
        String: la query à mettre en paramètre dans le executemany
        """
        query = ''
        when_matched = ''
        try:
            result_columns, indexes_tuple = self.build_insert_query(table_name=table_name, dataframe=dataframe,
                                                                    update=True)
            indexes_tuple = list(indexes_tuple)
            indexes_tuple[result_columns.index(primary_key)] = f"{sequence_name}.{seq_func}"
            indexes_tuple = tuple(indexes_tuple)

            if len(merge_id) == 1:
                merge_on = f"{merge_id[0]} = :{result_columns.index(merge_id[0]) + 1}"
            else:
                merge_on = ""
                for merge in merge_id:
                    merge_on += f"{merge} = :{result_columns.index(merge) + 1} AND "
                merge_on = merge_on[:-4]
            for index, column in enumerate(result_columns):
                if column not in merge_id and column not in primary_key:
                    when_matched += f"{column} = :{index + 1}, "
            when_matched = when_matched[:-2]

            query = f"""MERGE INTO {table_name} USING DUAL ON ({merge_on}) """
            query += f"""WHEN MATCHED THEN UPDATE SET {when_matched} """.replace("[", "").replace("]", "")
            query += f"""WHEN NOT MATCHED THEN INSERT {result_columns} VALUES {indexes_tuple}""".replace("'", "")
        except Exception as ex_log:
            logging.exception(f" Erreur lors de l'ajout des logs : {ex_log}")
        return query

    def delete_all(self, table_name):
        """
        Efface toutes les lignes de la table. Remplace le 'replace' de to_sql natif qui supprime la table

        Parameters
        ----------
        table_name: str
            Nom de la table à purger
        """

        try:
            conn = self.cx_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM " + table_name)
            conn.commit()
        except Exception as ex_del_all:
            logging.exception(f' Erreur lors de la supression des lignes de la table {table_name} : {ex_del_all}')
        finally:
            conn.close()  # noqa

    @staticmethod
    def add_logs(func):
        """
        Fonction (decoratrice) qui permet de logguer des resultat dans une table
        Parameters
        ----------
        func
        """

        def inner(*args, **kwargs):
            try:
                data, connection, cursor, log_table_name = func(*args, **kwargs)
                data = data.head(1)
                query = OracleDataBase.build_insert_query(table_name=log_table_name, dataframe=data)
                row = tuple(data.values[0])
                cursor.execute(query, row)
                connection.commit()
            except Exception as ex_log:
                logging.exception(f" Erreur lors de l'ajout des logs : {ex_log}")

        return inner

    @staticmethod
    def execute_and_commit(database_connection, cursor, df, query):
        # Création d'une liste de panda series
        rows = [tuple(x) for x in df.values]
        # Bulk insert et commit
        print(rows[0])
        cursor.executemany(query, [rows[0]])
        database_connection.commit()
        print('Data COMMITED')
