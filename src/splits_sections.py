import re
import json

from sections import SECTIONS

INPUT_PATH = "data/processed/ndps_full_text.txt"
OUTPUT_PATH = "data/processed/ndps_sections.json"

# opening the text file in read mode
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    full_text = f.read()

results = []

# looping through every section in SECTIONS
for i, (section_number, section_title, chapter_roman, chapter_name) in enumerate(SECTIONS):

    # taking the first 4 words of the section title
    title_start = " ".join(section_title.split()[:4])

    # searching for the section in the text
    pattern = (
        rf"(?m)^{re.escape(section_number)}\.\s+"
        rf".*?{re.escape(title_start)}"
    )

    match = re.search(pattern, full_text)

    if not match:
        print(f"Could not find section {section_number}: {section_title}")
        continue

    start_position = match.start()

    # finding the end position (start of next section)
    end_position = len(full_text)
    if i + 1 < len(SECTIONS):
        next_section_number, next_section_title, _, _ = SECTIONS[i + 1]
        next_title_start = " ".join(next_section_title.split()[:4])
        next_pattern = (
            rf"(?m)^{re.escape(next_section_number)}\.\s+"
            rf".*?{re.escape(next_title_start)}"
        )
        next_match = re.search(next_pattern, full_text[start_position:])
        if next_match:
            end_position = start_position + next_match.start()

    section_content = full_text[start_position:end_position].strip()

    results.append({
        "section_number": section_number,
        "title": section_title,
        "chapter": chapter_name,
        "chapter_roman": chapter_roman,
        "content": section_content
    })

# saving the results to JSON
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nSaved {len(results)} sections to {OUTPUT_PATH}")
