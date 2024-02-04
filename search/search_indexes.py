from elasticsearch_dsl import Document, Text, Keyword, Date



class ArticleIndex(Document):
    """
        Elasticsearch document definition for indexing articles.

        This class defines the structure of documents to be indexed in Elasticsearch for articles. It specifies the fields
        and their types to be indexed.

        Attributes:
            title (Text): Title of the article.
            author (Keyword): Author(s) of the article.
            institutions (Keyword): Institutions associated with the article.
            keywords (Keyword): Keywords related to the article.
            pdf_url (Keyword): URL to the PDF version of the article.
            bibliographie (Keyword): Bibliographic information of the article.
            abstract (Text): Abstract of the article.
            text (Text): Full text content of the article.
            date (Date): Publication date of the article.
            status (Text): Status of the article (e.g., 'published', 'unpublished').

        Class Attributes:
            Index (class): Inner class defining the name of the Elasticsearch index to be created for articles.
                name (str): Name of the Elasticsearch index ('article_index').
    """
    title = Text()
    author = Keyword()
    institutions = Keyword()
    keywords = Keyword()
    pdf_url = Keyword()
    bibliographie = Keyword()
    abstract = Text()
    text = Text()
    date = Date()
    status = Text()


    class Index:
        name = 'article_index'



class TestArticleIndex(Document):
    #same as the upper index but especially for the functional test
    title = Text()
    author = Keyword()
    institutions = Keyword()
    keywords = Keyword()
    pdf_url = Keyword()
    bibliographie = Keyword()
    abstract = Text()
    text = Text()
    date = Date()
    status = Text()

    class Index:
        name = 'test_article_index'