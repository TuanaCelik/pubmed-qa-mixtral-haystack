import streamlit as st
from haystack import Pipeline
from utils.pubmed_fetcher import PubMedFetcher
from haystack.components.generators import HuggingFaceTGIGenerator
from haystack.components.builders.prompt_builder import PromptBuilder

# def start_keyword_pipeline(llm):
#     keyword_prompt_template = """
# Your task is to convert the follwing question into 3 keywords that can be used to find relevant medical research papers on PubMed.
# Here is an examples:
# question: "What are the latest treatments for major depressive disorder?"
# keywords:
# Antidepressive Agents
# Depressive Disorder, Major
# Treatment-Resistant depression
# ---
# question: {{ question }}
# keywords:
# """
#     keyword_prompt_builder = PromptBuilder(template=keyword_prompt_template)

#     keyword_pipeline = Pipeline()
#     keyword_pipeline.add_component("keyword_prompt_builder", keyword_prompt_builder)
#     keyword_pipeline.add_component("keyword_llm", llm)
#     return keyword_pipeline

# def start_qa_pipeline(llm):
#     return qa_pipeline

def start_haystack(huggingface_token):
    #Use this function to contruct a pipeline
    llm = HuggingFaceTGIGenerator("mistralai/Mixtral-8x7B-Instruct-v0.1", token=huggingface_token)
    llm.warm_up()
    # start_keyword_pipeline(llm)
    # start_qa_pipeline(llm)
    keyword_prompt_template = """
Your task is to convert the follwing question into 3 keywords that can be used to find relevant medical research papers on PubMed.
Here is an examples:
question: "What are the latest treatments for major depressive disorder?"
keywords:
Antidepressive Agents
Depressive Disorder, Major
Treatment-Resistant depression
---
question: {{ question }}
keywords:
"""
    prompt_template = """
Answer the question truthfully based on the given documents.
If the documents don't contain an answer, use your existing knowledge base.

q: {{ question }}
Articles:
{% for article in articles %}
  {{article.content}}
  keywords: {{article.meta['keywords']}}
  title: {{article.meta['title']}}
{% endfor %}

"""
    keyword_prompt_builder = PromptBuilder(template=keyword_prompt_template)
    prompt_builder = PromptBuilder(template=prompt_template)
    fetcher = PubMedFetcher()

    pipe = Pipeline()

    pipe.add_component("keyword_prompt_builder", keyword_prompt_builder)
    pipe.add_component("keyword_llm", llm)
    pipe.add_component("pubmed_fetcher", fetcher)
    pipe.add_component("prompt_builder", prompt_builder)
    pipe.add_component("llm", llm)

    pipe.connect("keyword_prompt_builder.prompt", "keyword_llm.prompt")
    pipe.connect("keyword_llm.replies", "pubmed_fetcher.queries")

    pipe.connect("pubmed_fetcher.articles", "prompt_builder.articles")
    pipe.connect("prompt_builder.prompt", "llm.prompt")                                             
    return pipe


@st.cache_data(show_spinner=True)
def query(query, _pipeline):
    try:
        result = _pipeline.run(data={"keyword_prompt_builder":{"question":query},
                          "prompt_builder":{"question": query},
                          "llm":{"generation_kwargs": {"max_new_tokens": 500}}})
    except Exception as e:
        result = ["Please make sure you are providing a correct, public Mastodon account"]
    return result