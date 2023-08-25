from services.NewsService import NewsService


class NewsController:
    def __init__(self) -> None:
        self.news_service = NewsService()

    """
    return news without considering keywords
    """

    def getNews(self):
        return self.news_service.getNews()

    """
    return news based on certain keywords
    """

    def getNewsWithKeywords(self, user_keywords):
        return self.news_service.getNewsWithKeywords(user_keywords)

    """
    deal requests with wrong route
    """

    def notFound(self, error):
        return self.news_service.notFound(error)
