from flask import *
from controllers.NewsController import NewsController

routes = Blueprint("routes", __name__)
news_controller = NewsController()

"""
return news without considering keywords
"""


@routes.route("/news", methods=["GET"])
def getNews_route():
    return news_controller.getNews()


"""
return news based on certain keywords
"""


@routes.route("/news_keywords", methods=["GET"])
def getNewsWithKeywords_route():
    # get list of keywords as argument from User's request
    user_keywords = request.args.getlist("keywords")
    return news_controller.getNewsWithKeywords(user_keywords)


"""
deal requests with wrong route
"""


@routes.errorhandler(404)
def notFound_route(error):
    news_controller.notFound(error)
