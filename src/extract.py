import pdfplumber
import re
import json
import os

# Path to PDF (run from project root, so no ../ needed)

PDF_PATH = "data/raw/ndps_act.pdf"
OUTPUT_PATH = "data/processed/ndps_sections.json"

# Opening the PDF
pdf = pdfplumber.open(PDF_PATH)
print(f"Total pages: {len(pdf.pages)}")

# Extracting text from page 5 onwards (skip pages 1-4 which are table of contents)
all_text = []
for i in range(4, len(pdf.pages)):  # Index 4 = page 5
    text = pdf.pages[i].extract_text()
    if text:
        all_text.append(text)

pdf.close()

# Joining all pages into one continuous string
full_text = "\n".join(all_text)
print(f"Total characters extracted: {len(full_text)}")

# Cleaning amendment markers
# Removing opening markers like 1[ 2[ 3[
full_text = re.sub(r'\d+\[', '', full_text)
# Removing closing brackets after punctuation
full_text = re.sub(r'([.;:,])\]', r'\1', full_text)
# Removing standalone closing brackets surrounded by spaces
full_text = re.sub(r'\s\]\s', ' ', full_text)
# Removing amendment footnotes (lines starting with number + Ins. or Sub.)
full_text = re.sub(r'\n\d+\.\s+(?:Ins|Sub)\..*?(?=\n|$)', '', full_text)

# Verifying cleaning worked — print first 500 chars
print("\n--- FIRST 500 CHARS AFTER CLEANING ---")
print(full_text[:500])

# Saving the cleaned full text for now (split into sections next)
os.makedirs("data/processed", exist_ok=True)
with open("data/processed/ndps_full_text.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"\nSaved cleaned text to {OUTPUT_PATH}")
