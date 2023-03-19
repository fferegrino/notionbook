import os
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook
from slugify import slugify

import notionbooks
from notionbooks.api.notion_client import NotionClient

DATABASE_ID = "97ecfa4e50d1482787912199c709d680"
AUTH = os.getenv("NOTION_API_KEY")
OUTPUT = Path("output")

notion_version = os.getenv("NOTION_VERSION", notionbooks.__notion_version__)

notion_client = NotionClient(notion_api_key=AUTH, notion_version=notion_version)

database = notion_client.get_database(DATABASE_ID)
pages = notion_client.get_pages(DATABASE_ID, "Status", "Review")

OUTPUT.mkdir(exist_ok=True)


mapping = {
    "bold": "b",
    "italic": "i",
    "strikethrough": "s",
    "underline": "u",
    "code": "code",
}


def create_notebook_from_blocks(blocks, title):
    nb = new_notebook()
    for block in blocks:
        block_type = block["type"]
        if block_type == "code":
            language = block["code"]["language"]
            if language == "python":
                actual_code = block["code"]["rich_text"][0]["plain_text"]
                nb.cells.append(new_code_cell(actual_code))
        else:
            print(block_type)
            level = -1
            if block_type.startswith("heading"):
                level = int(block_type[-1])

            contents = block[block_type].get("text", block[block_type].get("rich_text", []))
            paragraph_content_tags = []
            for content in contents:
                if text := content.get("text"):
                    text_content = text["content"]
                    annotations = content["annotations"]
                    annotations = {annotation: annotations.get(annotation, False) for annotation in mapping.keys()}
                    for annotation, tag in mapping.items():
                        if annotations.get(annotation):
                            text_content = f"<{tag}>{text_content}</{tag}>"
                    if level > 0:
                        text_content = f"{'#' * level} {text_content}"
                        level = -1
                    paragraph_content_tags.append(text_content)
                elif equation := content.get("equation"):
                    paragraph_content_tags.append(f'${equation["expression"]}$')
            paragraph_content = " ".join(paragraph_content_tags)
            nb.cells.append(new_markdown_cell(paragraph_content))

    nbformat.write(nb, OUTPUT / f"{title}.ipynb")


for page in pages:
    title = page["properties"]["Name"]["title"][0]["text"]["content"]
    title_slug = slugify(title)
    blocks = notion_client.get_blocks(page["id"])
    create_notebook_from_blocks(blocks, title)
    # break
