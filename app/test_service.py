import unittest
import main 
from mock import patch
from mockupdatabasewithoutdata import MockDBWithOutData

class TestOfQuoatasService(MockDBWithOutData):

    def test_addUserToDB(self):
        with self.mock_db_config:
            # Test post data to dataBase
            respons = main.addUserToDB('bob4', 5, 10)

            self.assertEqual(respons.message, 'User limit information added')
            self.assertEqual(respons.status_code, 200)
    
    def test_deteleUserFromDB(self):
        with self.mock_db_config:
            user_id = 'bob1'
            respons = main.deteleUserFromDB(user_id)

            self.assertEqual(respons.message, "User " + user_id + " was deleted")
            self.assertEqual(respons.status_code, 200)
    
    def test_readFromDB(self):
        with self.mock_db_configForRead:
            user_id = 'bob2'
            respons = main.readFromDB(user_id)

            self.assertEqual(respons[0], 3)
            self.assertEqual(respons[1], 4)








#if __name__ == '__test_service.py__':
 #   unittest.main
    




    #The tests run in the following order, this is for every test_function (The test might not run in the order of the scrip)

    # setUp
    # Some test function
    # tearDown

    # This setup the fake muk up database. This setup a database for each function
    #def setUp(self):

    # This teardown the muck up database: This is the last thing that get runs
    #def tearDown(self):
