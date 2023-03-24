from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook
from slugify import slugify

from notionbooks.notion_to_jupyter.block_utils import get_content, is_python_code, mapping, prepend_item


def process_database(notion_client, database_id, output_path):
    output_path = Path(output_path)
    output_path.mkdir(exist_ok=True)
    pages = notion_client.get_pages(database_id, "Status", "Review")
    for page in pages:
        title = page["properties"]["Name"]["title"][0]["text"]["content"]
        title_slug = slugify(title)
        output_file = output_path / f"{title_slug}.ipynb"
        blocks = notion_client.get_blocks(page["id"])
        notebook = create_notebook_from_blocks(blocks, break_on_heading=True)
        notebook.metadata["notion_metadata"] = page
        with open(output_file, "w") as f:
            nbformat.write(notebook, f)


def create_notebook_from_blocks(blocks, break_on_heading=False):
    nb = new_notebook()
    total_blocks = len(blocks)
    current_block = 0
    while current_block < total_blocks:
        block = blocks[current_block]
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
    return nb


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
