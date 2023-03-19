import os

from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
import nbformat
from slugify import slugify

from notionbooks.api.notion_client import NotionClient
import notionbooks
from pathlib import Path

DATABASE_ID='97ecfa4e50d1482787912199c709d680'
AUTH=os.getenv("NOTION_API_KEY")
OUTPUT=Path('output')

notion_version = os.getenv("NOTION_VERSION", notionbooks.__notion_version__)

notion_client = NotionClient(notion_api_key=AUTH, notion_version=notion_version)

database = notion_client.get_database(DATABASE_ID)
pages = notion_client.get_pages(DATABASE_ID, "Status", "Review")

OUTPUT.mkdir(exist_ok=True)

def create_notebook_from_blocks(blocks, title):
    nb = new_notebook()
    for block in blocks:
        block_type = block["type"]
        if block_type == "code":
            language = block['code']['language']
            if language=='python':
                actual_code = block['code']['rich_text'][0]['plain_text']
                nb.cells.append(new_code_cell(actual_code))
        else:
            print(block_type)
            contents = block[block_type].get("text", block[block_type].get("rich_text", []))
            paragraph_content_tags = []
            for content in contents:
                if text := content.get("text"):
                    text_content = text["content"]
                    annotations = content["annotations"]
                    annotations_tags = ["bold", "italic", "strikethrough", "underline", "code"]
                    annotations = {
                        annotation:annotations.get(annotation, False) for annotation in annotations_tags
                    }
                    paragraph_content_tags.append(text_content)
                elif equation := content.get("equation"):
                    paragraph_content_tags.append(f'${equation["expression"]}$')
            paragraph_content = " ".join(paragraph_content_tags)
            nb.cells.append(new_markdown_cell(paragraph_content))
            pass

    nbformat.write(nb, OUTPUT/f"{title}.ipynb")


for page in pages:
    title = page["properties"]["Name"]["title"][0]["text"]["content"]
    title_slug = slugify(title)
    blocks = notion_client.get_blocks(page["id"])
    create_notebook_from_blocks(blocks, title)
    # break

