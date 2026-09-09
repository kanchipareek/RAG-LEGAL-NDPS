import re
import json

# Import the list of 129 sections we hardcoded in sections.py
from sections import SECTIONS

# Where to read the full Act text from, and where to save the output
INPUT_PATH = "data/processed/ndps_full_text.txt"
OUTPUT_PATH = "data/processed/ndps_sections.json"

# Read the entire Act text into one big string
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    full_text = f.read()

# This list will hold all our extracted sections
results = []

# Go through each section one by one (enumerate gives us both index i and the section data)
for i, (section_number, section_title, chapter_roman, chapter_name) in enumerate(SECTIONS):

    # Take only the first 4 words of the title to search for
    # Example: "Punishment for consumption of any narcotic drug" becomes "Punishment for consumption of"
    title_start = " ".join(section_title.split()[:4])

    # Some sections like 68I are printed as "68-I" in the PDF (with a hyphen)
    # So we need to handle that. If the section number ends with a letter (like I, A, B, O),
    # we allow an optional hyphen before the letter in our search
    if len(section_number) > 1 and section_number[-1].isalpha():
        # Split "68I" into "68" and "I", then search for "68I" OR "68-I"
        num_part = section_number[:-1]       # "68"
        alpha_part = section_number[-1]       # "I"
        search_number = rf"{num_part}-?{alpha_part}"  # "68-?I" means "68I" or "68-I"
    else:
        # Normal section number like "27" — just escape it for regex safety
        search_number = re.escape(section_number)

    # Build the regex pattern to find this section in the full text
    # It looks for: section number at start of line, then a period, then the first 4 words of title
    pattern = (
        rf"(?m)^{search_number}\.\s+"        # Section number + period at start of line
        rf".*?{re.escape(title_start)}"      # Followed by the first 4 words of title
    )

    # Search for the pattern (IGNORECASE means uppercase/lowercase doesn't matter)
    match = re.search(pattern, full_text, re.IGNORECASE)

    # If we can't find the section in the text...
    if not match:
        # Section 65 is marked as [Omitted] in the Act itself — there is no body text
        # So we add it manually with just that note
        if section_number == "65":
            results.append({
                "section_number": section_number,
                "title": section_title,
                "chapter": chapter_name,
                "chapter_roman": chapter_roman,
                "content": "65. [Omitted.]"
            })
            print(f"Section 65: [Omitted] - added manually")
        else:
            # For any other missing section, just print a warning and skip it
            print(f"Could not find section {section_number}: {section_title}")
        continue  # Skip to the next section in the loop

    # Found it! Note where this section starts in the full text
    start_position = match.start()

    # Now we need to find where this section ENDS
    # By default, assume it goes till the end of the entire text
    end_position = len(full_text)

    
    # But if there's a next section in our list, the current section ends where the next one starts
    # We might need to skip sections that don't exist in the text (like 65 [Omitted])
    if i + 1 < len(SECTIONS):
        # Look ahead through future sections until we find one that matches in the text
        for j in range(i + 1, len(SECTIONS)):
            next_section_number, next_section_title, _, _ = SECTIONS[j]
            next_title_start = " ".join(next_section_title.split()[:4])

            if len(next_section_number) > 1 and next_section_number[-1].isalpha():
                next_num_part = next_section_number[:-1]
                next_alpha_part = next_section_number[-1]
                next_search_number = rf"{next_num_part}-?{next_alpha_part}"
            else:
                next_search_number = re.escape(next_section_number)

            next_pattern = (
                rf"(?m)^{next_search_number}\.\s+"
                rf".*?{re.escape(next_title_start)}"
            )

            next_match = re.search(next_pattern, full_text[start_position:], re.IGNORECASE)
            if next_match:
                end_position = start_position + next_match.start()
                break  # Found the real end — stop looking


        # Same hyphen logic for the next section number
        if len(next_section_number) > 1 and next_section_number[-1].isalpha():
            next_num_part = next_section_number[:-1]
            next_alpha_part = next_section_number[-1]
            next_search_number = rf"{next_num_part}-?{next_alpha_part}"
        else:
            next_search_number = re.escape(next_section_number)

        # Build the same kind of pattern for the next section
        next_pattern = (
            rf"(?m)^{next_search_number}\.\s+"
            rf".*?{re.escape(next_title_start)}"
        )

        # Search for the next section AFTER the current section's start position
        next_match = re.search(next_pattern, full_text[start_position:], re.IGNORECASE)
        if next_match:
            # The end of current section = start of next section
            end_position = start_position + next_match.start()

    # Extract the text between start and end — that's our section's content
    section_content = full_text[start_position:end_position].strip()
        # Section 83 is the last section — it absorbs the Schedule (drug table)
    # Cut off everything after the actual section text ends
    if section_number == "83":
        # The Schedule starts with patterns like "SCHEDULE" or drug entries
        # Find where the real section 83 text ends (after clause (2))
        schedule_start = re.search(r'\n\s*(?:THE\s+)?SCHEDULE', section_content, re.IGNORECASE)
        if schedule_start:
            section_content = section_content[:schedule_start.start()].strip()
        else:
            # If no "SCHEDULE" keyword, look for the drug table pattern
            # Drug entries start with numbers followed by chemical names
            drug_table = re.search(r'\n\d+\.\s+[A-Z][A-Z]', section_content)
            if drug_table:
                section_content = section_content[:drug_table.start()].strip()


    # Save this section as a dictionary with all its metadata
    results.append({
        "section_number": section_number,
        "title": section_title,
        "chapter": chapter_name,
        "chapter_roman": chapter_roman,
        "content": section_content
    })

# Save all sections to a JSON file
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# Print how many sections we successfully saved
print(f"\nSaved {len(results)} sections to {OUTPUT_PATH}")
