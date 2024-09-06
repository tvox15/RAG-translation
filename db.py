from dotenv import load_dotenv
load_dotenv()
import os
from langchain_community.vectorstores import Chroma
from get_embedding_function import get_embedding_function

# This page is for simple queries to DB to verify if things were imported properly

CHROMA_PATH = os.environ['CHROMA_PATH']
DATA_PATH = os.environ['DATA_PATH']

db = Chroma(persist_directory=CHROMA_PATH,
                     embedding_function=get_embedding_function()
                    )

def main():
    db_values = db.get()
    print((db_values["ids"]))


if __name__ == "__main__":
    main()



 


