import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
import os 

from flaskr import create_app
from models import setup_db, Question, Category

# create a fresh testing database before starting tests
os.system('dropdb trivia_test')
os.system('createdb trivia_test')
os.system('psql trivia_test < trivia.psql')

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

        self.assertError(res, body, 404, 'page not found')
    
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

        self.assertError(res, body, 404, 'page not found')

        res = self.client().get('/categories/1000/questions')
        body = res.get_json()

        self.assertError(res, body, 422, 'category not found')
        
    def test_delete_question_by_id_success(self):
        res = self.client().delete('/questions/1')
        body = res.get_json()

        self.assertEquals(res.status_code, 200)
        self.assertTrue(body['success'])

        question = Question.query.get(1)
        
        self.assertFalse(question)

    def test_delete_question_by_id_fail(self):
        res = self.client().delete('/questions/1000')
        body = res.get_json()

        self.assertError(res, body, 404, 'question not found')

    def test_create_question_success(self):
        res = self.client().post('/questions', json={
            "question": "test question",
            "answer": "test answer",
            "category": 1,
            "difficulty": 3
        })
        body = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(body['success'])

    def test_create_question_fail(self):
        # all fields must be present
        res = self.client().post('/questions', json={
            "question": "test question"
        })
        body = res.get_json()
        self.assertError(res, body, 400, 'question, answer, difficulty and category must be provided')

        # difficulty and category must be numbers
        res = self.client().post('/questions', json={
            "question": "test questions",
            "answer": "test answer",
            "category": "c",
            "difficulty": "d"
        })
        body = res.get_json()
        self.assertError(res, body, 400, 'difficulty and category must be numbers')

        # difficulty must be between 1 and 5
        res = self.client().post('/questions', json={
            "question": "test questions",
            "answer": "test answer",
            "category": 1,
            "difficulty": 10
        })
        body = res.get_json()
        self.assertError(res, body, 400, 'difficulty must be between 1 and 5')
        
        # category must exit
        res = self.client().post('/questions', json={
            "question": "test questions",
            "answer": "test answer",
            "category": 1000,
            "difficulty": 3
        })
        body = res.get_json()
        self.assertError(res, body, 400, 'category doesn\'t exists')

    def test_search_questions_success(self):
        res = self.client().post('/questions/searches', json={
            "searchTerm": "movie"
        })
        body = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(body['success'])
        self.assertTrue(body['questions'])
        self.assertEqual(body['questions'][0]['id'], 3)

    def test_search_questions_fail(self):
        res = self.client().post('/questions/searches', json={})
        body = res.get_json()
        self.assertError(res, body, 400, 'request doesn\'t have searchTerm')

    def test_get_quizzes_success(self):
        res = self.client().post('/quizzes', json={
            "previous_questions": [12, 13],
            "quiz_category": {
                "id": 2,
                "type": "Art"
            }
        })
        body = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(body['success'])
        self.assertTrue(body['question'])
        self.assertEqual(body['question']['category'], 2)
    
        # if quiz_category id equals 0 this means all categories
        res = self.client().post('/quizzes', json={
            "previous_questions": [1, 2],
            "quiz_category": {
                "id": 0,
                "type": "all"
            }
        })
        body = res.get_json()
        self.assertEqual(res.status_code, 200)

    def test_get_quizzes_fail(self):
        res = self.client().post('/quizzes', json={})
        body = res.get_json()
        self.assertError(res, body, 400, 'previous_questions and quiz_category must be provided')

        # quiz category id must be valid 
        res = self.client().post('/quizzes', json={
            "previous_questions": [],
            "quiz_category": {
                "id": 222,
                "type": "Art"
            }
        })
        body = res.get_json()
        self.assertError(res, body, 400, 'category doesn\'t exist')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()