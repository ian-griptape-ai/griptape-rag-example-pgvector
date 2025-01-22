import os

from dotenv import load_dotenv
from griptape.chunkers import PdfChunker
from griptape.drivers import OpenAiEmbeddingDriver, PgVectorVectorStoreDriver
from griptape.loaders import PdfLoader
from griptape.structures import Agent
from griptape.tools import VectorStoreTool
from griptape.utils import Chat
import time
import concurrent.futures

# Get environment variables
load_dotenv()
DB_PASSWORD = os.environ.get("DB_PASSWORD")

# Set pgvector variables
db_user = "username"
db_pass = DB_PASSWORD
db_host = "localhost"
db_port = "5432"
db_name = "postgres"


def process_item(item):
    # process items. item is a tuple with the pdf file path and the namespace
    print(f"Processing tuple: {item}")
    print(f"Loading PDF: {item[0]}")
    pdf_artifact = PdfLoader().load(item[0])
    print(f"Chunking PDF: {item[0]}")
    chunks = PdfChunker(max_tokens=500).chunk(pdf_artifact)
    print(f"Upserting chunks from: {item[0]} in namespace: {item[1]}")
    vector_store_driver.upsert_text_artifacts({item[1]: chunks})


# define function to process a list in threads
def process_list_in_threads(items):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_item, item) for item in items]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # Retrieve the result to catch any exceptions
            except Exception as e:
                print(f"An error occurred: {e}")


# Create the connetion string
db_connection_string = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

# Create the PgVectorVectorStoreDriver
vector_store_driver = PgVectorVectorStoreDriver(
    connection_string=db_connection_string,
    embedding_driver=OpenAiEmbeddingDriver(),
    table_name="vectors",
)

# Install required Postgres extensions and create database schema
vector_store_driver.setup()


documents_to_upsert = [  # list your PDF documents here. Each tuple should contain a PDF file path and a namespace.
    ("vector-test/document1.pdf", "document1"),
    ("vector-test/document2.pdf", "document2"),
]

if True:
    print("Upserting documents in threads, one thread per document")
    t1 = time.perf_counter()  # Start the timer
    process_list_in_threads(documents_to_upsert)
    t2 = time.perf_counter()  # Stop the timer
    print(t2 - t1, "Completed with {} seconds elapsed")  # Print the time elapsed

# Create the tool
tool = VectorStoreTool(
    vector_store_driver=vector_store_driver,
    description="This DB has information about the judgement and the strikeout application",
)

# Create the agent
agent = Agent(tools=[tool], stream=True)

# Run the agent
Chat(agent).start()
