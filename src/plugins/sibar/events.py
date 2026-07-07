from utils.logger import get_logger

logger = get_logger(__name__)


def on_article_submitted(**kwargs):
    article = kwargs.get("article")
    logger.debug("Sibar: article %s submitted, awaiting workflow stage.", article)
