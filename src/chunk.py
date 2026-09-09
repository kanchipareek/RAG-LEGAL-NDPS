import json
import re

INPUT_PATH = "data/processed/ndps_sections.json"
OUTPUT_PATH = "data/processed/ndps_chunks.json"

# Load the sections JSON
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    sections = json.load(f)

# Empty list of chunks
chunks = []

# Loop through each section
for section in sections:
    content = section["content"]
    section_number = section["section_number"]

    # If section is short enough, keep it as 1 chunk
    if len(content) <= 1500:
        chunks.append({
            "chunk_id": f"{section_number}-1",
            "section_number": section_number,
            "title": section["title"],
            "chapter": section["chapter"],
            "chapter_roman": section["chapter_roman"],
            "content": content
        })

 # If section is long, split it by sub-clauses
    else:
        # Split on patterns like (1), (2), (a), (b), (i), (ii) at start of line
        # re.split keeps the delimiter if we use a capture group
        sub_chunks = re.split(r'\n(?=\([a-z0-9]+\))', content)

# If splitting didn't help (only 1 piece), split by double newlines
        if len(sub_chunks) <= 1:
            sub_chunks = content.split('\n\n')

        # If STILL only 1 piece, just split at 1500 chars at nearest space
        if len(sub_chunks) <= 1:
            words = content.split(' ')
            sub_chunks = []
            current = ""
            for word in words:
                if len(current) + len(word) + 1 > 1500:
                    sub_chunks.append(current.strip())
                    current = word
                else:
                    current += " " + word
            if current:
                sub_chunks.append(current.strip())

        
               # Add each sub-chunk with an incrementing number
        # But first, merge tiny chunks (under 50 chars) into the previous one
        merged = []
        for sub_content in sub_chunks:
            sub_content = sub_content.strip()
            if not sub_content:
                continue
            # If this chunk is tiny and we have a previous chunk, merge it
            if len(sub_content) < 50 and merged:
                merged[-1] = merged[-1] + " " + sub_content
            else:
                merged.append(sub_content)

        for idx, sub_content in enumerate(merged, 1):
            chunks.append({

                "chunk_id": f"{section_number}-{idx}",
                "section_number": section_number,
                "title": section["title"],
                "chapter": section["chapter"],
                "chapter_roman": section["chapter_roman"],
                "content": sub_content
            })

# Save to JSON
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

# Print stats
lengths = [len(c["content"]) for c in chunks]
print(f"Total chunks: {len(chunks)}")
print(f"Average chunk length: {sum(lengths) // len(lengths)} chars")
print(f"Longest chunk: {max(lengths)} chars")
print(f"Shortest chunk: {min(lengths)} chars")
print(f"Saved to {OUTPUT_PATH}")


        