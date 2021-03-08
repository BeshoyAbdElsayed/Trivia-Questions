import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}@{}/{}".format('postgres:password', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # helper functions
    def assertError(self, res, body, code, message):
        self.assertEqual(res.status_code, code)
        self.assertFalse(body['success'])
        self.assertEqual(body['error'], code)
        self.assertEqual(body['message'], message)


    def test_get_categories(self):
        res = self.client().get('/categories')
        body = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(body['categories'])

    def test_get_all_questions_success(self):
        res = self.client().get('/questions')
        body = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(body['success'])
        self.assertTrue(body['questions'])
        self.assertTrue(body['total_questions'])
        
    def test_get_all_questions_fail(self):
        res = self.client().get('/questions?page=1000')
        body = res.get_json()

        self.assertError(res, body, 404, 'resource not found')
    
    def test_get_questions_by_category_success(self):
        res = self.client().get('/categories/1/questions')
        body = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(body['success'])
        self.assertTrue(body['questions'])
        self.assertTrue(body['total_questions'])
        self.assertEqual(body['current_category'], 1)

    def test_get_questions_by_category_fail(self):
        res = self.client().get('/categories/1/questions?page=1000')
        body = res.get_json()

        self.assertError(res, body, 404, 'resource not found')

        res = self.client().get('/categories/1000/questions')
        body = res.get_json()

        self.assertError(res, body, 422, 'unprocessable')
        
        

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()