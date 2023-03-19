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


def is_python_code(block):
    return block["type"] == "code" and block["code"]["language"].lower() == "python"


def create_notebook_from_blocks(blocks, title, break_on_heading=False):
    nb = new_notebook()
    total_blocks = len(blocks)
    current_block = 0
    while current_block < total_blocks:
        block = blocks[current_block]
        block_type = block["type"]
        if is_python_code(block):
            actual_code = block["code"]["rich_text"][0]["plain_text"]
            nb.cells.append(new_code_cell(actual_code))
        else:
            contents = [block]
            while current_block + 1 < total_blocks and not is_python_code(blocks[current_block + 1]):
                if break_on_heading and blocks[current_block + 1]["type"].startswith("heading"):
                    break
                current_block += 1
                next_block = blocks[current_block]
                contents.append(next_block)
            nb.cells.append(new_markdown_cell(process_blocks(contents)))
        current_block += 1
    nbformat.write(nb, OUTPUT / f"{title}.ipynb")


def get_content(block):
    block_type = block["type"]
    return block[block_type]["rich_text"]


def prepend_item(block):
    block_type = block["type"]
    if block_type == "bulleted_list_item":
        return " - "
    elif block_type == "numbered_list_item":
        return " 1. "
    elif block_type == "callout":
        return f" > {block['callout']['icon']['emoji']} "
    elif block_type.startswith("heading"):
        return ("#" * int(block["type"][-1])) + " "
    return ""


def process_blocks(blocks):
    cell_content = []
    for block in blocks:
        contents = get_content(block)
        prepend_content = prepend_item(block)
        final_content = process_content(contents)
        paragraph_content = prepend_content + final_content
        cell_content.append(paragraph_content)
    return "\n\n".join(cell_content)


def process_content(contents):
    paragraph_content_tags = []
    for content in contents:
        if text := content.get("text"):
            text_content = text["content"]
            annotations = content["annotations"]
            annotations = {annotation: annotations.get(annotation, False) for annotation in mapping.keys()}
            for annotation, tag in mapping.items():
                if annotations.get(annotation):
                    text_content = f"<{tag}>{text_content}</{tag}>"
            paragraph_content_tags.append(text_content)
        elif equation := content.get("equation"):
            paragraph_content_tags.append(f'${equation["expression"]}$')
        final_content = "".join(paragraph_content_tags)
    return final_content


for page in pages:
    title = page["properties"]["Name"]["title"][0]["text"]["content"]
    title_slug = slugify(title)
    blocks = notion_client.get_blocks(page["id"])
    create_notebook_from_blocks(blocks, title, break_on_heading=True)
