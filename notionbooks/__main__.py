import os

import typer

import notionbooks
from notionbooks.api.notion_client import NotionClient
from notionbooks.notion_to_jupyter import process_database

app = typer.Typer()


@app.command()
def notion_jupyter():
    database_id = "97ecfa4e50d1482787912199c709d680"
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_version = os.getenv("NOTION_VERSION", notionbooks.__notion_version__)
    notion_client = NotionClient(notion_api_key=notion_api_key, notion_version=notion_version)
    process_database(notion_client, database_id, "output")


# Run the app
if __name__ == "__main__":
    app()
