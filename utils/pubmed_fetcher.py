from pymed import PubMed
from typing import List
from haystack import component
from haystack import Document

pubmed = PubMed(tool="Haystack2.0Prototype", email="tilde.thurium@deepset.ai")

def documentize(article):
  return Document(content=article.abstract, meta={'title': article.title, 'keywords': article.keywords})

@component
class PubMedFetcher():

  @component.output_types(articles=List[Document])
  def run(self, queries: list[str]):
    cleaned_queries = queries[0].strip().split('\n')

    articles = []
    try:
      for query in cleaned_queries:
        response = pubmed.query(query, max_results = 1)
        documents = [documentize(article) for article in response]
        articles.extend(documents)
    except Exception as e:
        print(e)
        print(f"Couldn't fetch articles for queries: {queries}" )
    results = {'articles': articles}
    return results