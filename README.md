# griptape-rag-example-pgvector
A short sample showing how to use Griptape with pgvector

Using the sample

1. Make sure you have access to a postgres database with pgvector installed
2. Copy .envsample to .env, updating your OpenAI API key and database password to the correct values
3. Update pgvector-sample.py to:
    1. set your db name, db username, host and port to the correct values
    2. update the list of documents to upsert to point at the PDF documents that you want to vectorize and upsert into your database
    3. Update the description attribute in the VectorStoreTool to contain a summary of the topics covered within the documents that you are going to upsert
4. Run the sample, you can now ask questions about the contents of the documents 