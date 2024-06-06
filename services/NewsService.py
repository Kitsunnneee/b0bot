import os
import json
from dotenv import dotenv_values
from flask import jsonify
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import HuggingFaceEndpoint

from models.NewsModel import CybernewsDB
env_vars = dotenv_values(".env")
HUGGINGFACEHUB_API_TOKEN = env_vars.get("HUGGINGFACE_TOKEN")
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN
class NewsService:
    def __init__(self) -> None:
        self.db = CybernewsDB()
        repo_id = "mistralai/Mistral-7B-Instruct-v0.2" # loading the llm

        self.llm = HuggingFaceEndpoint(
                repo_id=repo_id, temperature=0.5, token=HUGGINGFACEHUB_API_TOKEN
            )
        self.news_format = "title [source, date(MM/DD/YYYY), news url];"
        self.news_number = 10

    """
    Return news while checking if keyword has been specified or not
    """

    def getNews(self, user_keywords=None):
    # Fetch news data from db:
    # Only fetch data with valid `author` and `newsDate`
    # Drop field "id" from collection
        news_data = self.db.get_news_collections().find(
            {"author": {"$ne": "N/A"}, "newsDate": {"$ne": "N/A"}},
            {
                "headlines": 1,
                "newsDate": 1,
                "author": 1,
                "newsURL": 1,
                "_id": 0,
            },
        )
        news_data = list(news_data)

        template = """Question: {question}
        Answer: Let's think step by step."""

        prompt = PromptTemplate.from_template(template)

        # Determine which messages template to load
        if user_keywords:
            messages_template_path = 'prompts/withkey.json'
        else:
            messages_template_path = 'prompts/withoutkey.json'
       
        # Load the messages template from the JSON file
        messages = self.load_json_file(messages_template_path)

        # Replace placeholders in the messages
        for message in messages:
            if message['role'] == 'user' and '<news_data_placeholder>' in message['content']:
                message['content'] = message['content'].replace('<news_data_placeholder>', str(news_data))
            if user_keywords and message['role'] == 'user' and '<user_keywords_placeholder>' in message['content']:
                message['content'] = message['content'].replace('<user_keywords_placeholder>', str(user_keywords))
            if message['role'] == 'user' and '{news_format}' in message['content']:
                message['content'] = message['content'].replace('{news_format}', self.news_format)
            if message['role'] == 'user' and '{news_number}' in message['content']:
                message['content'] = message['content'].replace('{news_number}', str(self.news_number))

        # Create the LLMChain with the prompt and llm
        llm_chain = LLMChain(prompt=prompt, llm=self.llm)
        output = llm_chain.invoke(messages)

        # Convert news data into JSON format
        news_JSON = self.toJSON(output['text'])

        return news_JSON

 
    """
    deal requests with wrong route
    """

    def notFound(self, error):
        return jsonify({"error": error}), 404
    
    """
    Load JSON file
    """
    
    def load_json_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    """
    Convert news given by Huggingface endpoint API into JSON format.
    """

    def toJSON(self, data: str):
        if len(data) == 0:
            return {}
        news_list = data.split("\n")
        news_list_json = []
        news_list.pop(0)
        for item in news_list:
            # Avoid dirty data
            if len(item) == 0:
                continue
            # Split the string at the first occurrence of '('
            if "[" in item:
                title, remaining = item.split("[", 1)
            else:
                title = item
                remaining = ""
            title = title.strip(' "')
            # Extract the source by splitting at ',' and removing leading/trailing whitespace
            if "," not in remaining:
                source = "N/A"
                date = "N/A"
                url = "N/A"
            else:
                parts = remaining.split(",")

                source = "N/A"
                date = "N/A"
                url = "N/A"

                # Update values if they are present
                if len(parts) > 0:
                    source = parts[0].strip(' "')
                if len(parts) > 1:
                    date = parts[1].strip(' "')
                if len(parts) > 2:
                    url = parts[2].strip(" ];")

            # Create a dictionary for each news item and append it to the news_list
            news_item = {
                "title": title,
                "source": source,
                "date": date,
                "url": url,
            }
            news_list_json.append(news_item)
  

        return jsonify(news_list_json)
