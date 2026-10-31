import docx
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import docx.opc.constants

def style_run(run, font_name="Times New Roman", size_pt=10.5, bold=False, italic=False, color_rgb=(0, 0, 0), underline=False):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.underline = underline
    run.font.color.rgb = RGBColor(*color_rgb)

def set_cell_text(cell, text, bold=False, italic=False, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.text = text
    p = cell.paragraphs[0]
    p.alignment = align
    for run in p.runs:
        style_run(run, size_pt=size_pt, bold=bold, italic=italic)

def set_cell_hyperlink(cell, url, text, size_pt=10.0, align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.text = "" # Clear plain text
    p = cell.paragraphs[0]
    p.alignment = align
    
    part = p.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    r = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')

    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), 'Times New Roman')
    rFonts.set(qn('w:hAnsi'), 'Times New Roman')
    rPr.append(rFonts)

    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), str(int(size_pt * 2)))
    rPr.append(sz)

    color = OxmlElement('w:color')
    color.set(qn('w:val'), '0563C1') # Standard clean hyperlink blue
    rPr.append(color)

    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rPr.append(u)

    r.append(rPr)
    
    t = OxmlElement('w:t')
    t.text = text
    r.append(t)
    
    hyperlink.append(r)
    p._p.append(hyperlink)

def copy_cell_border(src_cell, dst_cell):
    tcPr_src = src_cell._tc.get_or_add_tcPr()
    tcBorders_src = tcPr_src.find(qn('w:tcBorders'))
    if tcBorders_src is not None:
        tcPr_dst = dst_cell._tc.get_or_add_tcPr()
        import copy
        tcPr_dst.append(copy.deepcopy(tcBorders_src))

def update_document(docx_path):
    print(f"Updating {docx_path}...")
    doc = docx.Document(docx_path)
    
    # 1. Cover Page / Title Header updates
    doc.paragraphs[3].text = "ISWE302L Artificial Inteligence"
    p3 = doc.paragraphs[3]
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p3.runs:
        style_run(run, size_pt=12, bold=True)

    doc.paragraphs[4].text = "Class ID : VL2026270101829"
    p4 = doc.paragraphs[4]
    p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p4.runs:
        style_run(run, size_pt=12, bold=False)

    doc.paragraphs[5].text = "Review - II (Final Review)"
    p5 = doc.paragraphs[5]
    p5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p5.runs:
        style_run(run, size_pt=12, bold=True)

    doc.paragraphs[6].text = "Date: 13/10/2026"
    p6 = doc.paragraphs[6]
    p6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p6.runs:
        style_run(run, size_pt=12, bold=False)

    doc.paragraphs[8].text = "24MIS0216 - Vivek Pandey"
    p8 = doc.paragraphs[8]
    p8.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p8.runs:
        style_run(run, size_pt=12, bold=True)

    doc.paragraphs[9].text = "24MIS0050 - S. Hemal"
    p9 = doc.paragraphs[9]
    p9.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p9.runs:
        style_run(run, size_pt=12, bold=True)

    doc.paragraphs[10].text = "24MIS0204 - Jay Prakash"
    p10 = doc.paragraphs[10]
    p10.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p10.runs:
        style_run(run, size_pt=12, bold=True)

    # 2. Table 6: Division of Work and Skills
    t6 = doc.tables[6]
    set_cell_text(t6.rows[1].cells[0], "1", bold=False, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(t6.rows[1].cells[1], "Vivek Pandey", bold=True, size_pt=10.5)
    set_cell_text(t6.rows[1].cells[2], "24MIS0216", bold=False, size_pt=10)
    set_cell_text(
        t6.rows[1].cells[3],
        "Backend Architecture & AI/ML Vision Pipeline: Built FastAPI backend microservices, Ultralytics YOLOv11 Nano object detection pipeline, 512-dim PyTorch visual embedding extractor, FAISS vector search engine, and multi-objective hybrid recommendation scoring algorithm.",
        bold=False, size_pt=10
    )
    set_cell_text(
        t6.rows[1].cells[4],
        "Python, PyTorch, FastAPI, Machine Learning algorithms, Vector search concepts.",
        bold=False, size_pt=10
    )
    set_cell_text(
        t6.rows[1].cells[5],
        "Ultralytics YOLOv11 deployment, FAISS IndexFlatIP inner-product vector indexing, L2 normalization, FastAPI asynchronous orchestration, tensor-based Non-Maximum Suppression (NMS).",
        bold=False, size_pt=10
    )

    set_cell_text(t6.rows[2].cells[0], "2", bold=False, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(t6.rows[2].cells[1], "S. Hemal", bold=True, size_pt=10.5)
    set_cell_text(t6.rows[2].cells[2], "24MIS0050", bold=False, size_pt=10)
    set_cell_text(
        t6.rows[2].cells[3],
        "Frontend UI Development & Desktop Shell: Built modern, responsive user interface using React 18, TypeScript, and Vite; integrated interactive Leaflet/OpenStreetMap geospatial views with radius filter slider; designed short-form video player with clickable bounding-box drawers; packaged standalone Windows executable via Electron v33.",
        bold=False, size_pt=10
    )
    set_cell_text(
        t6.rows[2].cells[4],
        "HTML/CSS, JavaScript, React fundamentals, Web design.",
        bold=False, size_pt=10
    )
    set_cell_text(
        t6.rows[2].cells[5],
        "TypeScript, Vite bundler, Leaflet OpenStreetMap geospatial mapping, Lucide React UI design, Electron desktop packaging and IPC bridge communication.",
        bold=False, size_pt=10
    )

    if len(t6.rows) < 4:
        r_jay = t6.add_row()
    else:
        r_jay = t6.rows[3]
    set_cell_text(r_jay.cells[0], "3", bold=False, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(r_jay.cells[1], "Jay Prakash", bold=True, size_pt=10.5)
    set_cell_text(r_jay.cells[2], "24MIS0204", bold=False, size_pt=10)
    set_cell_text(
        r_jay.cells[3],
        "Database Architecture, Persistence & Automated Testing: Designed relational database schema using SQLite 3 and SQLAlchemy ORM; engineered binary FAISS index file serialization and metadata mapping; implemented seed dataset ingestion pipelines for multi-city merchants and products; authored and verified comprehensive 46-test automated pytest validation suite.",
        bold=False, size_pt=10
    )
    set_cell_text(
        r_jay.cells[4],
        "SQL, Relational Database Management Systems (RDBMS), Python basics.",
        bold=False, size_pt=10
    )
    set_cell_text(
        r_jay.cells[5],
        "SQLAlchemy ORM modeling, SQLite database management, FAISS vector persistence and indexing optimization, synthetic data generation, Pytest automated testing and regression validation.",
        bold=False, size_pt=10
    )

    # 3. Table 7 & Table 8: Phases and Plan
    t7 = doc.tables[7]
    set_cell_text(t7.rows[1].cells[1], "4 Structured Project Phases", bold=True, size_pt=10.5)

    t8 = doc.tables[8]
    set_cell_text(t8.rows[1].cells[0], "Phase 1: Project Initiation, Architecture & Prototype Demo", bold=True, size_pt=10)
    set_cell_text(t8.rows[1].cells[1], "Requirement analysis, literature survey, system architecture design, database schema definition, and baseline prototype demonstration (Aligned with Review 1).", bold=False, size_pt=10)
    set_cell_text(t8.rows[1].cells[2], "19/08/2026 – 01/09/2026", bold=False, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(t8.rows[1].cells[3], "Completed", bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)

    set_cell_text(t8.rows[2].cells[0], "Phase 2: AI Vision Pipeline & FAISS Vector Indexing", bold=True, size_pt=10)
    set_cell_text(t8.rows[2].cells[1], "Ultralytics YOLOv11 Nano object detection integration, 512-dim PyTorch embedding extraction, and FAISS vector index persistence.", bold=False, size_pt=10)
    set_cell_text(t8.rows[2].cells[2], "02/09/2026 – 16/09/2026", bold=False, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(t8.rows[2].cells[3], "Completed", bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)

    set_cell_text(t8.rows[3].cells[0], "Phase 3: Backend Services, Geospatial Engine & Database Modeling", bold=True, size_pt=10)
    set_cell_text(t8.rows[3].cells[1], "FastAPI REST microservices, SQLAlchemy ORM persistence, Haversine spherical proximity calculations, and explainable fraud rules.", bold=False, size_pt=10)
    set_cell_text(t8.rows[3].cells[2], "17/09/2026 – 30/09/2026", bold=False, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(t8.rows[3].cells[3], "Completed", bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)

    if len(t8.rows) < 5:
        r4 = t8.add_row()
        for c in r4.cells:
            copy_cell_border(t8.rows[3].cells[0], c)
    else:
        r4 = t8.rows[4]
    set_cell_text(r4.cells[0], "Phase 4: Frontend UI, System Integration & Final Testing", bold=True, size_pt=10)
    set_cell_text(r4.cells[1], "React/TypeScript UI development, Leaflet map integration, comprehensive 46-test Pytest verification, Electron standalone packaging, and final review submission (Aligned with Review 2).", bold=False, size_pt=10)
    set_cell_text(r4.cells[2], "01/10/2026 – 13/10/2026", bold=False, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(r4.cells[3], "Completed", bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)

    # 4. Table 10 & Table 11: Review History (Keep ONLY 2 Reviews!)
    t10 = doc.tables[10]
    set_cell_text(t10.rows[1].cells[1], "2 Reviews (Review I, Review II)", bold=True, size_pt=10.5)

    t11 = doc.tables[11]
    set_cell_text(t11.rows[1].cells[0], "Review 1", bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(t11.rows[1].cells[1], "19/08/2026", bold=False, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(
        t11.rows[1].cells[2],
        "Project Introduction + Demo: Clarify problem statement, define system scope, evaluate edge vs. cloud AI feasibility, and demonstrate initial prototype.",
        bold=False, size_pt=10
    )
    set_cell_text(
        t11.rows[1].cells[3],
        "Presented project introduction and early interactive video prototype; adopted edge-first Ultralytics YOLOv11 Nano and local CPU FAISS vector search to eliminate cloud API costs.",
        bold=False, size_pt=10
    )

    set_cell_text(t11.rows[2].cells[0], "Review 2", bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(t11.rows[2].cells[1], "13/10/2026", bold=False, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(
        t11.rows[2].cells[2],
        "Complete Implementation: Comprehensive end-to-end evaluation across frontend UI, AI vision pipeline, backend orchestration, database persistence, and automated testing.",
        bold=False, size_pt=10
    )
    set_cell_text(
        t11.rows[2].cells[3],
        "Delivered complete system implementation: integrated React/TypeScript frontend with FastAPI backend, Haversine local discovery, explainable fraud detection, 46 automated passing pytest cases, and standalone Electron desktop packaging.",
        bold=False, size_pt=10
    )

    while len(t11.rows) > 3:
        tr = t11.rows[3]._element
        tr.getparent().remove(tr)

    # 5. Table 13: Pitch and Outcomes
    t13 = doc.tables[13]
    set_cell_text(t13.rows[1].cells[0], "GitHub / Professional Platform", bold=True, size_pt=10)
    
    # EMBED ACTIVE WORD HYPERLINK OBJECT FOR 100% DEVICE COMPATIBILITY
    set_cell_hyperlink(t13.rows[1].cells[1], "https://github.com/vivek41754-tech/scrollix", "https://github.com/vivek41754-tech/scrollix", size_pt=10.0)
    set_cell_text(t13.rows[1].cells[2], "Completed", bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)

    set_cell_text(t13.rows[2].cells[0], "Patent", bold=True, size_pt=10)
    set_cell_text(t13.rows[2].cells[1], "Edge-First Multimodal Video Commerce with Geospatial Vector Ranking", bold=False, size_pt=10)
    set_cell_text(t13.rows[2].cells[2], "Planned", bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)

    set_cell_text(t13.rows[3].cells[0], "Publication", bold=True, size_pt=10)
    set_cell_text(
        t13.rows[3].cells[1],
        "Paper titled 'Scrollix AI: Bridging Video Discovery and Local Commerce with Edge Computer Vision' prepared for conference submission.",
        bold=False, size_pt=10
    )
    set_cell_text(t13.rows[3].cells[2], "Planned", bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)

    set_cell_text(t13.rows[4].cells[0], "Startup", bold=True, size_pt=10)
    set_cell_text(t13.rows[4].cells[1], "Hyperlocal commerce enablement tool for local artisan clusters in urban areas.", bold=False, size_pt=10)
    set_cell_text(t13.rows[4].cells[2], "Planned", bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)

    set_cell_text(t13.rows[5].cells[0], "Any Other Plan", bold=True, size_pt=10)
    set_cell_text(t13.rows[5].cells[1], "Publishing open-source installer and sample dataset generator for academic use.", bold=False, size_pt=10)
    set_cell_text(t13.rows[5].cells[2], "Planned", bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)

    doc.save(docx_path)
    print(f"Successfully updated and saved {docx_path}")

if __name__ == '__main__':
    targets = [
        r"C:\Users\vivek\Downloads\Scrollix_AI_Project_Report_Clean.docx",
        r"c:\Users\SCROLL\Scrollix_AI_Project_Report.docx"
    ]
    for p in targets:
        try:
            update_document(p)
        except Exception as e:
            print(f"Error updating {p}: {e}")
