

#import lib

#https://www.freshersworld.com/

import os
import requests
import json
from typing import List
from bs4 import BeautifulSoup
from IPython.display import Markdown, display, update_display
from openai import OpenAI
import langchain_community
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from openai import OpenAI
#from langchain.schema import Document
from langchain_core.documents.base import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
import glob
import gradio
from dotenv import load_dotenv
load_dotenv()
MODEL = "gpt-4o-mini"
db_name = "vector_db"
import os
openai=OpenAI(api_key=os.getenv('openai_api_key'))



# A class to represent a Webpage

class Website:
    """
    A utility class to represent a Website that we have scraped, now with links
    """

    def __init__(self, url=None,drive=None):

        self.url = url if url is not None else {}
        # Check if the URL is valid before making the request
        if isinstance(url, str) and url.startswith("http"):  
            response = requests.get(url)
            self.body = response.content
            soup = BeautifulSoup(self.body, 'html.parser')
            self.title = soup.title.string if soup.title else "No title found"
            if soup.body:
                for irrelevant in soup.body(["script", "style", "img", "input"]):
                    irrelevant.decompose()
                self.text = soup.body.get_text(separator="\n", strip=True)
            else:
                self.text = ""
            links = [link.get('href') for link in soup.find_all('a')]
            self.links = [link for link in links if link]
        else:
            # Handle invalid URL, e.g., by setting empty values or raising an exception
            self.body = ""
            self.title = "Invalid URL"
            self.text = ""
            self.links = []

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"

    def links_imp(object):
        user_prompt = f"these r all the links available {object.url} -"
        user_prompt += "Only take out important links from all the links above respond with full https url in json format.\n Do not include Terms of Service, Privacy, email links."
        user_prompt += "\n relative use-full links \n"
        user_prompt += "\n".join(object.links)
        return user_prompt

    def get_links(self, url):
        website = Website(url)
        link_system_prompt = "You are provided with a list of links found on a webpage. \
        You are able to decide which of the links would be most relevant to include in a brochure about the company, \
        such as links to an About page, or a Company page, or Careers/Jobs pages.\n"
        link_system_prompt += "You should respond in JSON as in this example:"
        link_system_prompt += """
         {
        "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page": "url": "https://another.full.url/careers"}
         ]
         }"""
        response = openai.chat.completions.create(
            model=MODEL,  # Make sure MODEL is defined
            messages=[
                {"role": "system", "content": link_system_prompt},
                {"role": "user", "content": website.links_imp()}, # changed links_imp(website) to website.links_imp() to make it an instance method call
                {'role': 'user', 'content': 'only return the url where type="jobs page" nothing else and return only the "url" nothing else'}
            ],
            response_format={"type": "text"}
        )
        result = response.choices[0].message.content
        return result
    def md(self,url,drive):
       content=Website(url)
       sd=content.text
       print('content',sd)
       print('document print starting....')
       with open(drive + 'job1.md','x') as f:
         f.write(sd)
       print('document print completed....')

if __name__ == '__main__':
    # Provide a valid URL as an argument
    import sys
    #url = "https://stackoverflow.com/"  # Replace with your desired URL
    url=sys.argv[1]
    drive=sys.argv[2]
    web = Website(url, drive)
    web.md(url, drive)
  
