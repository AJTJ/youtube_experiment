import youtube_methods
import chromadb
from chromadb import Collection
import os
from dotenv import load_dotenv


load_dotenv()


def main():

    chroma_client = chromadb.Client()
    # persisted eventually: client = chromadb.PersistentClient(path="/path/to/save/to")
    # https://docs.trychroma.com/guides

    collection: Collection = chroma_client.create_collection(name="my_collection")
    youtube_methods.create_video_output(collection)


if __name__ == "__main__":
    main()
