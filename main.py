import os
import shutil
import openai 
import time

from dotenv import load_dotenv
load_dotenv()


from get_embedding_function import get_embedding_function
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain.schema import Document
from langchain_community.vectorstores import Chroma


openai.api_key = os.environ['OPENAI_API_KEY']
CHROMA_PATH = os.environ['CHROMA_PATH']
DATA_PATH = os.environ['DATA_PATH']

def main():
    init_db_with_docs()

def init_db_with_docs():
    docs = load_documents()
    split_docs = split_documents(docs)
    add_to_chroma(split_docs)
    
def load_documents():
    loader = DirectoryLoader(DATA_PATH, 
                             glob="*.xls", 
                             loader_cls=UnstructuredExcelLoader,
                             )
    docs = loader.load()
    return docs

def split_documents(docs: list[Document]):
    split_docs = []

    for doc in docs:
        text = doc.page_content
        chunks = text.split("\n\n\n")[2:]

        # for each split chunk, split by \n and turn to json formatted by:
        # { idx, start_tc, end_tc, source_lang, target_lang}
        
        split_doc = []
        for _, chunk in enumerate(chunks):
            split_chunk = chunk.split("\n")
            if len(split_chunk) == 5:
                split_doc.append({
                    "idx": split_chunk[0],
                    "start_tc": split_chunk[1],
                    "end_tc": split_chunk[2],
                    "source_lang": split_chunk[3],
                    "target_lang": split_chunk[4]
                })

        # we want to save it back to doc.page_content as 10 lines of source_lang, 10 lines of target_lang, separated by \n
        # and overlapped by 5 lines
        
        start_range = 0
        end_range = 10
        page = 0
        while end_range < len(split_doc):
            str = ""
            for i in range(start_range, end_range):
                str += split_doc[i]["source_lang"] + " "
            str += "\n"
            for i in range(start_range, end_range):
                str += split_doc[i]["target_lang"] + " "
            str += "\n\n"
            start_range += 5
            end_range += 5
            backslash_char = "\\"

            # This parses the filename from the filepath and removes extension
            id = f"{doc.metadata['source'].split(backslash_char)[-1].split('.')[0]}:{page}"
            new_doc = Document(
                page_content = str,
                metadata = {
                    "source": doc.metadata["source"],
                    "page": page,
                    "id": id
                }
            )
            split_docs.append(new_doc)
            page += 1

    return split_docs

def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


def add_to_chroma(chunks: list[Document]):

    
    #Load the existing database.
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    #Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB by checking matching IDs
    new_chunks = []
    for chunk in chunks:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    # add 1 doc every .2 seconds to avoid rate limit
    for i, chunk in enumerate(new_chunks):
        print(f"Adding document {i+1}/{len(new_chunks)}")
        db.add_documents([chunk])
        db.persist()
        time.sleep(0.2)

    else:
        print("✅ No new documents to add")



if __name__ == "__main__":
    main()
