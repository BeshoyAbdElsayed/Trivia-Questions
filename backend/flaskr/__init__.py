import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from random import random
from math import floor

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]
    return jsonify({
      "success": True,
      "categories": formatted_categories
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_all_questions():
    all_questions = Question.query.all()
    categories = Category.query.all()
    current_questions = paginate_questions(request, all_questions)
    if len(current_questions) == 0:
      abort(404, 'page not found')
    return jsonify({
      "success": True,
      "questions": current_questions,
      "total_questions": len(all_questions),
      "categories": [category.format() for category in categories],
      "current_category": 0
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question_by_id(question_id):
    question = Question.query.get(question_id)
    if not question:
      abort(404, 'question not found')
    
    question.delete()
    return jsonify({
      "success": True,
    })


  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_new_question():
    data = request.get_json()
    # validate data exits
    if 'question' not in data or 'answer' not in data or 'difficulty' not in data or 'category' not in data:
      abort(400, 'question, answer, difficulty and category must be provided')

    # validate difficulty and category is a number 
    try:
      difficulty = int(data['difficulty'])
      category_id = int(data['category'])
    except:
      abort(400, 'difficulty and category must be numbers')

    # validate difficulty from 1 to 5
    if not (1 <= difficulty <= 5):
      abort(400, 'difficulty must be between 1 and 5')

    # validate category exists
    category = Category.query.get(category_id)
    if not category:
      abort(400, 'category doesn\'t exists')
    
    # create question
    question = Question(
      question   = data['question'],
      answer     = data['answer'],
      category   = category_id,
      difficulty = difficulty 
    )
    question.insert();

    return jsonify({
      "success": True,
      "created": question.id
    })


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/searches', methods=['POST'])
  def search_questions_by_name():
    data = request.get_json()
    # validate there is a search term
    if 'searchTerm' not in data:
      abort(400, 'request doesn\'t have searchTerm')
    
    search_term = data['searchTerm']
    questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    formatted_quesions = [question.format() for question in questions]
    return jsonify({
      "success": True,
      "questions": formatted_quesions
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_category_questions(category_id):
    questions = Question.query.filter(Question.category == category_id).all()
    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]
    if not questions:
      abort(422, 'category not found')

    current_questions = paginate_questions(request, questions)
    if len(current_questions) == 0:
      abort(404, 'page not found')

    return jsonify({
      "success": True,
      "questions": current_questions,
      "total_questions": len(questions),
      "categories": formatted_categories,
      "current_category": category_id
    })
    

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quiz_question():
    data = request.get_json()
    # make sure data is correct
    if 'previous_questions' not in data or 'quiz_category' not in data:
      abort(400, 'previous_questions and quiz_category must be provided')
    previous_questions = data['previous_questions']
    quiz_category_id = int(data['quiz_category']['id'])
    # validate category exists
    # category id = 0 means all categories
    if quiz_category_id != 0:
      category = Category.query.get(quiz_category_id)
      if not category:
        abort(400, 'category doesn\'t exist')
    
    # get all questions
    if quiz_category_id == 0:
      all_questions = Question.query.all()
    else:
      all_questions = Question.query.filter(Question.category==quiz_category_id)
    
    # get questions pool from all questions execluding prvious questions
    questions_pool = []
    for question in all_questions:
      if question.id not in previous_questions:
        questions_pool.append(question)

    # if questions pool is empty retrun empty question dict
    if len(questions_pool) == 0:
      random_question = {}
    else:
      # get a random question from the questions pool 
      random_index = floor(random() * len(questions_pool))
      random_question = questions_pool[random_index].format()

    return jsonify({
      "success": True,
      "question": random_question
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": error.description
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": error.description
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": error.description 
      }), 400
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": error.description 
    }), 405
  
  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": error.description 
    }), 500

  return app

    