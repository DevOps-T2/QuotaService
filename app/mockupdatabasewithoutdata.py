import unittest
# from unittest import TestCase
import mysql.connector
from mysql.connector import errorcode
from mock import patch
import main


MYSQL_HOST = "localhost"
MYSQL_DB = "test_db"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""



# This is created in the beginning of the tests
class MockDBWithOutData(unittest.TestCase):
    
    
    @classmethod
    def setUpClass(cls):
        cnx = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        cursor = cnx.cursor(dictionary=True)

        # drop database if it already exists
        try:
            cursor.execute("DROP DATABASE {}".format(MYSQL_DB))
            cursor.close()
            print("DB dropped")
        except mysql.connector.Error as err:
            print("{}{}".format(MYSQL_DB, err))

        cursor = cnx.cursor(dictionary=True)
        try:
            sql = "CREATE DATABASE {}".format(MYSQL_DB)
            print(sql)
            cursor.execute(
                "CREATE DATABASE {}".format(MYSQL_DB))
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)

        cnx.database = MYSQL_DB

        query = """CREATE TABLE quotas (
                id INTEGER NOT NULL AUTO_INCREMENT,
                user_id VARCHAR(255) NOT NULL,
                memory INTEGER NOT NULL,
                vcpus INTEGER NOT NULL,
                UNIQUE(user_id),
                PRIMARY KEY (id)
                )"""
        try:
            cursor.execute(query)
            cnx.commit()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("test_table already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

        insert_data_query = """INSERT INTO `quotas` (`user_id`, `memory`, `vcpus`) VALUES
                            ('bob1', '1', 2),
                            ('bob2', '3',4),
                            ('bob3', '5',6)"""
        try:
            cursor.execute(insert_data_query)
            cnx.commit()
        except mysql.connector.Error as err:
            print("Data insertion to test_table failed \n" + err)
        cursor.close()
        cnx.close()

        testconfig ={
            'host': MYSQL_HOST,
            'user': MYSQL_USER,
            'database': MYSQL_DB
        }
        cls.mock_db_config = patch.dict(main.configForWrite, testconfig)
        cls.mock_db_configForRead = patch.dict(main.configForRead, testconfig)


    @classmethod
    def tearDownClass(cls):
        cnx = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER
        )
        cursor = cnx.cursor(dictionary=True)

        # drop test database
        try:
            cursor.execute("DROP DATABASE {}".format(MYSQL_DB))
            cnx.commit()
            cursor.close()
        except mysql.connector.Error as err:
            print("Database {} does not exists. Dropping db failed".format(MYSQL_DB))
        cnx.close()    