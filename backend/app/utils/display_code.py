def extract_code_blocks(filepath):
    code = []
    inside_block = False
    with open(filepath, "r") as f:
        for line in f:
            if line.strip().startswith("```python"):
                inside_block = True
                continue
            elif line.strip().startswith("```"):
                inside_block = False
                continue
            if inside_block:
                code.append(line)
    return "".join(code)
