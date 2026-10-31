import docx

doc = docx.Document(r'C:/Users/vivek/.gemini/antigravity/brain/16d77359-8caf-4589-b84e-05ff77f6de7c/.user_uploaded/media_1792414868871_9f4723f7.docx')

print("--- PARAGRAPHS WITH PLACEHOLDERS ---")
for i, p in enumerate(doc.paragraphs):
    if "{{" in p.text or "}}" in p.text or "Review" in p.text or "Date" in p.text or "Course" in p.text or "Title" in p.text:
        print(f"P[{i}]: {repr(p.text)}")

print("\n--- TABLES WITH PLACEHOLDERS ---")
for ti, table in enumerate(doc.tables):
    for ri, row in enumerate(table.rows):
        for ci, cell in enumerate(row.cells):
            if "{{" in cell.text or "}}" in cell.text:
                print(f"T[{ti}] R[{ri}] C[{ci}]: {repr(cell.text)}")
