
from pathlib import Path
output_file = Path("merged.txt")
txt_files = sorted(Path(".").glob("*.txt"))

with output_file.open("w", encoding="utf-8") as outfile:
    for file in txt_files:
        content = file.read_text(encoding="utf-8")
        outfile.write(content)
