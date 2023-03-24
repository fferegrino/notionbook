def is_python_code(block):
    return block["type"] == "code" and block["code"]["language"].lower() == "python"


def prepend_item(block):
    """Prepend the block with the appropriate tag depending on the type of block"""
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


def get_content(block):
    """Get the content of a block"""
    try:
        if block["type"] == "equation":
            return [block["equation"]]
        else:
            block_type = block["type"]
            return block[block_type]["rich_text"]
    except KeyError:
        print(f"Block type {block_type} not supported")
        return {}


mapping = {
    "bold": "b",
    "italic": "i",
    "strikethrough": "s",
    "underline": "u",
    "code": "code",
}
