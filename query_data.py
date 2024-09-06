from dotenv import load_dotenv
load_dotenv()
import os

from get_embedding_function import get_embedding_function
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Add each line into the array here
query_text_lines = [
 
]

PROMPT_TEMPLATE = """
Translate the following subtitles from Korean to English based on the following context.
The translation must sound natural in spoken form to native english speakers.
Each line must be BELOW 52 characters including spaces.
It's for a young audience, so be be fun and engaging! use exclamation marks, but no emojis or tildes.
If sentences continues through multiple lines, then the translation CAN cross multiple lines.
Use context to determine if the sentence is continuing or if it is a new sentence.
Between each line, add \n to separate the lines.
Sentences MUST in proper punctuation (period, question mark, exclamation mark).
Remember, they are talking TO each other on the screen, so it MUST sound natural.
Don't translate the speaker's name (the part before the colon)

CONTEXT:
{context}
---

Translate this text based on the above context: {question}

If there is no context, use your own knowledge to translate the line.
"""


CHROMA_PATH = os.environ['CHROMA_PATH']

def main():
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())

    context_text = ""
    for query_text in query_text_lines:
        results = db.similarity_search_with_relevance_scores(query_text, k=3)
        #commenting this out to unclutter the output
        # if len(results) == 0 or results[0][1] < 0.7:
           # print(f"Unable to find matching results. Sending without context.")        
        context_text += "\n\n---\n\n".join([doc.page_content for doc, _score in results]) + "\n\n---\n\n"

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question="\n".join(query_text_lines))
    model = ChatOpenAI()
    response_text = model.invoke(prompt)

    # comment this out to unclutter the output
    # sources = [doc.metadata.get("source", None) for doc, _score in results]
    # formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(response_text.content)

if __name__ == "__main__":
    main()