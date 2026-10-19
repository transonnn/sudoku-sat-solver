import csv
import statistics
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
REPORT_DIR = ROOT / "report"
OUTPUT = REPORT_DIR / "sudoku_solver_report.docx"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def add_word_field(paragraph, field_code):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = field_code
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = "Open in Word to update this field"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for element in (begin, instruction, separate, placeholder, end):
        run._r.append(element)


def read_csv(path):
    if not path.exists():
        print(f"WARNING: Missing CSV: {path}")
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def set_cell_text(cell, text, bold=False):
    cell.text = str(text)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.bold = bold
            run.font.name = "Times New Roman"
            run.font.size = Pt(9)


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, header in enumerate(headers):
        set_cell_text(table.rows[0].cells[i], header, True)
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            set_cell_text(cells[i], value)
    doc.add_paragraph()
    return table


def add_figure(doc, path, caption, width=5.8):
    if not path.exists():
        doc.add_paragraph(f"[Figure unavailable: {path.name}]")
        print(f"WARNING: Missing figure: {path}")
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(width))
    p = doc.add_paragraph(caption)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p.runs:
        run.italic = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(9)


def fmt_seconds(value):
    return f"{value:.4f}"


def add_bullet(doc, text):
    return doc.add_paragraph(text, style="List Bullet")


def add_code_line(doc, command):
    p = doc.add_paragraph()
    r = p.add_run(command)
    r.font.name = "Consolas"
    r.font.size = Pt(9)


def add_hyperlink(paragraph, text, url, font_size=12):
    relationship_id = paragraph.part.relate_to(
        url,
        RT.HYPERLINK,
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), relationship_id)

    run = OxmlElement("w:r")
    properties = OxmlElement("w:rPr")
    run_style = OxmlElement("w:rStyle")
    run_style.set(qn("w:val"), "Hyperlink")
    properties.append(run_style)
    size = OxmlElement("w:sz")
    size.set(qn("w:val"), str(font_size * 2))
    properties.append(size)
    run.append(properties)

    text_element = OxmlElement("w:t")
    text_element.text = text
    run.append(text_element)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


doc = Document()
section = doc.sections[0]
section.page_width = Inches(8.27)
section.page_height = Inches(11.69)
section.top_margin = Inches(0.85)
section.bottom_margin = Inches(0.85)
section.left_margin = Inches(0.9)
section.right_margin = Inches(0.9)
styles = doc.styles
styles["Normal"].font.name = "Times New Roman"
styles["Normal"].font.size = Pt(11)
styles["Normal"].paragraph_format.space_after = Pt(6)
styles["Normal"].paragraph_format.line_spacing = 1.08
for name in ("Title", "Heading 1", "Heading 2"):
    styles[name].font.name = "Times New Roman"
styles["Heading 1"].font.color.rgb = RGBColor(0, 0, 0)
styles["Heading 1"].font.size = Pt(13)
styles["Heading 2"].font.size = Pt(11)

# CAS-style front matter: title, title note, author, correspondence, credit,
# abstract, highlights, and keywords.
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.LEFT
p.paragraph_format.space_after = Pt(5)
p.paragraph_format.keep_with_next = True
r = p.add_run(
    "Comparative Study of Sudoku Solvers: SAT, CP-SAT, "
    "Mixed-Integer Programming, and Scaled Instances"
)
r.bold = True
r.font.name = "Times New Roman"
r.font.size = Pt(18)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.LEFT
p.paragraph_format.space_after = Pt(10)
p.paragraph_format.keep_with_next = True
r = p.add_run(
    "¹"
)
r.font.superscript = True
r.font.size = Pt(9)
r = p.add_run(
    " Project report describing the Sudoku solvers and experimental results "
    "available in the associated repository."
)
r.font.name = "Times New Roman"
r.font.size = Pt(9)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.LEFT
p.paragraph_format.space_after = Pt(3)
p.paragraph_format.keep_with_next = True
r = p.add_run("Tran Cam Son")
r.bold = True
r.font.name = "Times New Roman"
r.font.size = Pt(12)
r = p.add_run("*")
r.font.superscript = True
r.font.size = Pt(9)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.LEFT
p.paragraph_format.space_after = Pt(3)
p.paragraph_format.keep_with_next = True
r = p.add_run("Corresponding author: ")
r.italic = True
r.font.name = "Times New Roman"
r.font.size = Pt(9)
r = p.add_run("24021615@vnu.edu.vn")
r.font.name = "Times New Roman"
r.font.size = Pt(9)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.LEFT
p.paragraph_format.space_after = Pt(3)
p.paragraph_format.keep_with_next = True
r = p.add_run("Author contributions: ")
r.bold = True
r.font.name = "Times New Roman"
r.font.size = Pt(9)
r = p.add_run(
    "Conceptualization, methodology, software, data curation, experiments, "
    "validation, analysis, and writing."
)
r.font.name = "Times New Roman"
r.font.size = Pt(9)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.LEFT
p.paragraph_format.space_after = Pt(2)
p.paragraph_format.keep_with_next = True
r = p.add_run("ABSTRACT")
r.bold = True
r.font.name = "Times New Roman"
r.font.size = Pt(10)
doc.add_paragraph(
    "This project studies several approaches to solving Sudoku as a constraint "
    "satisfaction problem. The methods evaluated on standard 9×9 Sudoku are "
    "Boolean satisfiability (SAT), Google OR-Tools CP-SAT, IBM CPLEX mixed-integer "
    "programming (MIP), IBM CPLEX constraint programming (CP), and Gurobi MIP. "
    "The 9×9 evaluation contains 30 generated instances, with 10 in each of three "
    "groups. Additional experiments use 16×16 and 25×25 Sudoku instances and "
    "compare SAT, CP-SAT, CPLEX MIP, and Gurobi. A separate SAT experiment "
    "compares pairwise and sequential-counter at-most-one encodings on the same "
    "standard puzzles. The benchmark records five measured runs per standard "
    "puzzle after a warm-up; scaled runs are single end-to-end measurements and "
    "have no explicit timeout in the runner. All 150 standard solver records and "
    "80 scaled records in the current CSV files are present, and all scaled "
    "records are marked solved and valid. On the scaled 25×25 set, however, "
    "observed solver times vary substantially, including long-running MIP "
    "instances. Results are descriptive of these datasets, formulations, and "
    "software configurations; they do not establish a universal ranking of "
    "solver technologies."
)

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(5)
p.paragraph_format.space_after = Pt(2)
p.paragraph_format.keep_with_next = True
r = p.add_run("HIGHLIGHTS")
r.bold = True
r.font.name = "Times New Roman"
r.font.size = Pt(10)
for highlight in [
    "Five solver implementations are compared on 30 standard 9×9 puzzles.",
    "Pairwise and sequential-counter AMO encodings are measured on identical inputs.",
    "Scaled experiments evaluate 16×16 and 25×25 puzzles with four solvers.",
    "Runtime summaries are computed from repository CSVs and interpreted with explicit scope limits.",
]:
    p = add_bullet(doc, highlight)
    p.paragraph_format.space_after = Pt(1)

p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(8)
r = p.add_run("Keywords: ")
r.bold = True
r.font.name = "Times New Roman"
r.font.size = Pt(9)
r = p.add_run("Sudoku; SAT; CNF; CP-SAT; mixed-integer programming; constraint programming; benchmarking; scalability.")
r.font.name = "Times New Roman"
r.font.size = Pt(9)

doc.add_heading("1. Introduction", level=1)
doc.add_paragraph(
    "A Sudoku puzzle is a finite constraint satisfaction problem: each cell "
    "must receive one symbol, and each row, column, and subgrid must satisfy a "
    "set of uniqueness rules. Although the rules are easy to state, they admit "
    "multiple encodings with substantially different representations. A SAT "
    "solver sees Boolean clauses; a constraint-programming (CP) solver can "
    "reason over integer domains and global all-different constraints; and a "
    "mixed-integer programming (MIP) solver works with binary variables and "
    "linear equalities. The problem therefore provides a compact case study in "
    "modeling choices and solver behavior, rather than a universal proxy for "
    "industrial optimization [1, 2]."
)
doc.add_paragraph(
    "The project implements these formulations in Python, checks returned "
    "boards against Sudoku rules, and records wall-clock measurements. Its "
    "standard dataset has 30 9×9 instances divided into easy, medium, and hard "
    "groups. The repository also contains separate pairwise-versus-sequential "
    "SAT measurements and scaled datasets of 16×16 and 25×25 puzzles. The "
    "comparison is intentionally empirical: differences in model construction, "
    "presolve, propagation, branching, and solution extraction all contribute "
    "to the observed call time."
)
doc.add_heading("1.1 Research questions", level=2)
for question in [
    "How do the five implemented solver configurations compare on the same 9×9 puzzles when runtime is summarized per instance?",
    "Does the sequential-counter encoding improve measured SAT time over pairwise AMO on this dataset, and is that effect consistent across puzzle groups?",
    "How do the four scaled-benchmark solvers behave when puzzle size increases from 16×16 to 25×25?",
    "Which features of the experiment—sample size, time protocol, model formulation, and recorded environment—limit generalization?",
]:
    add_bullet(doc, question)

doc.add_heading("1.2 Scope and interpretation", level=2)
doc.add_paragraph(
    "The report covers solver wrappers and benchmark outputs present in this "
    "repository at generation time. It does not treat the benchmark CSV as a "
    "controlled multi-machine study, nor does it infer a causal explanation "
    "for a solver's speed from a runtime ranking alone. In particular, the "
    "easy/medium/hard labels are dataset categories and clue counts, not an "
    "independent human-difficulty score. The scaled benchmark is a distinct "
    "experiment and should not be pooled with the standard 9×9 results."
)
doc.add_paragraph(
    "All times are wall-clock durations measured around a Python solver call. "
    "They should therefore be read as the time needed by these implementations "
    "to build a model, invoke the selected engine, and extract a solution on "
    "the recorded machine. They are not pure search-node or propagation costs. "
    "The benchmark validates solutions immediately after the timer stops; "
    "validation time is not part of the reported solver duration."
)

doc.add_heading("2. Report design and contributions", level=1)
doc.add_paragraph(
    "The manuscript follows the supplied CAS-style article organization: title "
    "and author block, abstract, highlights, keywords, numbered sections, "
    "experimental findings, discussion, limitations, data availability, "
    "references, and reproducibility appendices. The body is tailored to the "
    "artifacts in this Sudoku repository rather than copying the N-Queens "
    "subject matter of the reference manuscript."
)
doc.add_paragraph(
    "The concrete contributions represented by the current code and data are:"
)
for contribution in [
    "A SAT encoding for square-box Sudoku, with pairwise and sequential-counter at-most-one constraints exposed through the solver API.",
    "Integer-domain CP-SAT and CPLEX CP formulations, and binary MIP formulations for CPLEX and Gurobi.",
    "A standard 9×9 benchmark runner that warms each solver once, records five timed repetitions per puzzle, and stores each puzzle's median.",
    "A separate AMO benchmark that compares the two implemented SAT encodings using the same puzzle set and repetition policy.",
    "A scaled-puzzle loader and benchmark that maps symbols to integer values, validates solutions, and records per-run status and time.",
    "Plotting scripts and tests that support inspection and reproduction of the recorded comparisons.",
]:
    add_bullet(doc, contribution)
doc.add_paragraph(
    "These contributions are bounded by what the code actually implements. "
    "For example, the AMO experiment does not evaluate Commander, Product, or "
    "Binary encodings, and the scaled experiment does not include CPLEX CP. "
    "The report distinguishes those implementation facts from possibilities "
    "for later experiments."
)

doc.add_heading("3. Background and related work", level=1)
doc.add_heading("3.1 Sudoku as a constraint satisfaction problem", level=2)
doc.add_paragraph(
    "A constraint satisfaction problem consists of variables, domains, and "
    "constraints. In an N×N Sudoku, each cell is a variable with domain "
    "{1,…,N}; row, column, and box rules are global uniqueness constraints. "
    "Equivalently, every digit must occur exactly once in each of N rows, N "
    "columns, and N boxes. This dual description—one value per cell versus one "
    "occurrence per unit—helps expose different encodings. A 9×9 puzzle has "
    "81 cell variables in the integer model, but a direct Boolean encoding "
    "uses 9³ candidate variables before auxiliary variables are introduced."
)
doc.add_paragraph(
    "A solution is a complete assignment satisfying all constraints and all "
    "clues. The solver is not asked to optimize a score: the objective is "
    "feasibility. A puzzle may have no solution, one solution, or multiple "
    "solutions unless uniqueness is established separately. Consequently, "
    "the fact that a solver returns a valid board proves that one solution was "
    "found; it does not by itself prove the puzzle has a unique solution."
)

doc.add_heading("3.2 Boolean satisfiability and cardinality", level=2)
doc.add_paragraph(
    "SAT asks whether a Boolean formula has a satisfying truth assignment. "
    "The project uses conjunctive normal form (CNF), a conjunction of clauses, "
    "where each clause is a disjunction of literals. Modern conflict-driven "
    "clause-learning solvers repeatedly make decisions, propagate implications, "
    "analyze conflicts, and learn clauses [1, 4]. The formula's representation can "
    "strongly influence the solver's propagation and search behavior; a smaller "
    "formula is not automatically easier to solve."
)
doc.add_paragraph(
    "Sudoku's exactly-one condition combines an at-least-one (ALO) clause with "
    "an at-most-one (AMO) encoding. For a candidate set X={x₁,…,xₖ}, ALO is the "
    "single clause (x₁ ∨ … ∨ xₖ). Pairwise AMO adds (¬xᵢ ∨ ¬xⱼ) for every "
    "i<j, requiring k(k−1)/2 binary clauses and no new variables. A sequential "
    "counter uses auxiliary variables to encode the running count and grows "
    "linearly in k. The trade-off is between formula size, auxiliary-variable "
    "overhead, and the propagation/search structure induced by the clauses [3]."
)
doc.add_paragraph(
    "This repository implements only pairwise and sequential-counter AMO "
    "choices in the SAT solver. The AMO benchmark uses the same solver engine "
    "and changes the encoding, which is a useful controlled comparison. It "
    "does not isolate clause count from all other factors: the number of "
    "auxiliary variables and the shape of the implication graph also change [5]."
)

doc.add_heading("3.3 Constraint programming and MIP", level=2)
doc.add_paragraph(
    "Constraint programming expresses finite-domain variables and relations "
    "directly. A global all-different constraint states that a collection of "
    "variables must take distinct values; specialized propagation can reason "
    "about the collection as a whole rather than decomposing it into every "
    "pairwise inequality. OR-Tools CP-SAT combines integer constraint modeling "
    "with SAT-based search and propagation. In this project, rows, columns, "
    "and boxes are represented as all-different groups."
)
doc.add_paragraph(
    "Mixed-integer programming represents discrete decisions using linear "
    "equalities and integrality restrictions. The Sudoku model uses a binary "
    "indicator for each cell-digit assignment. Equality constraints enforce "
    "one selected digit per cell and one occurrence of each digit per row, "
    "column, and box. Feasibility is expressed with a constant objective. "
    "Although the mathematical constraints are equivalent across engines, "
    "the solvers have different presolve, branching, cut generation, and "
    "propagation implementations; a benchmark compares the complete systems [6–9]."
)

doc.add_heading("4. Problem statement and mathematical model", level=1)
doc.add_heading("4.1 Generalized Sudoku", level=2)
doc.add_paragraph(
    "Let the grid have size N×N, where N=q² for a positive integer q. Each "
    "cell (r,c), with 0≤r,c<N, receives one value from {1,…,N}. Every row, "
    "column, and q×q "
    "subgrid must contain each symbol exactly once. Given clues are fixed to "
    "their original values. The repository's solvers infer square boxes from "
    "N using the integer square root; a size such as 16 uses 4×4 boxes, while "
    "25 uses 5×5 boxes."
)
doc.add_paragraph(
    "Before constraints are applied, N^(N²) complete assignments are possible "
    "if every cell independently chooses one of N values. This is a raw "
    "combinatorial upper count, not the number of legal grids or the number "
    "of solutions to a particular clue pattern. The all-different and clue "
    "constraints eliminate nearly all such assignments, and search difficulty "
    "depends on the puzzle structure and solver."
)

doc.add_heading("4.2 Constraint equations", level=2)
doc.add_paragraph(
    "Let x[r,c,v] be a binary indicator equal to one exactly when cell (r,c) "
    "contains value v. For every cell, the candidate indicators sum to one. "
    "For every fixed row, column, or box and every value, the indicators over "
    "that unit also sum to one:"
)
for formula in [
    "Cell:  Σ(v=1..N) x[r,c,v] = 1,                 for every r,c.",
    "Row:   Σ(c=0..N−1) x[r,c,v] = 1,               for every r,v.",
    "Column:Σ(r=0..N−1) x[r,c,v] = 1,               for every c,v.",
    "Box:   Σ((r,c) in box b) x[r,c,v] = 1,         for every box b and v.",
    "Clue:  x[r,c,given[r,c]] = 1,                  for every non-empty clue.",
]:
    add_code_line(doc, formula)
doc.add_paragraph(
    "There are N³ primary binary indicators in this formulation. The cell, "
    "row-digit, column-digit, and box-digit families each contribute N² "
    "exactly-one constraints, for 4N² structural groups, before the clue "
    "restrictions. In the code, each clue is also posted as a singleton "
    "exactly-one constraint in the MIP adapters or as a unit clause in SAT. "
    "The linear feasibility model has no meaningful optimization criterion; "
    "the wrappers use a constant objective solely to invoke the MIP API."
)
doc.add_paragraph(
    "For an integer-domain model, each cell variable y[r,c] has domain "
    "{1,…,N}. Every row, column, and box is constrained to be all-different, "
    "and each clue fixes the corresponding variable to a constant. These "
    "constraints express the same feasible set as the binary model, using "
    "different variables and propagation mechanisms."
)

doc.add_heading("4.3 A small encoding example", level=2)
doc.add_paragraph(
    "Consider a 4×4 Sudoku with 2×2 boxes. The direct SAT representation has "
    "4³=64 primary variables. Variable x[0,0,1] denotes the proposition that "
    "the upper-left cell contains 1; x[0,0,2], x[0,0,3], and x[0,0,4] denote "
    "its other candidates. The ALO clause for that cell is their four-way "
    "disjunction. Pairwise AMO adds six binary clauses, one for every pair "
    "of candidates. The sequential-counter alternative adds auxiliary "
    "variables and clauses to prevent two of the four candidates from being "
    "true simultaneously."
)
doc.add_paragraph(
    "The same cell participates in more than one exactly-one group. For "
    "example, x[0,0,1] is also a candidate in the group requiring digit 1 "
    "exactly once in row 0, the group requiring digit 1 exactly once in "
    "column 0, and the group requiring digit 1 exactly once in the upper-left "
    "2×2 box. These overlapping groups are how the SAT encoding couples local "
    "cell choices to global row, column, and box rules. If the puzzle clue at "
    "(0,0) is 1, a positive unit clause forces x[0,0,1] true; AMO clauses then "
    "force the other three candidates for that cell false."
)
doc.add_paragraph(
    "This miniature example describes the encoding pattern, not a benchmark "
    "instance in the report. It also illustrates why a single cell-level "
    "constraint is insufficient: correctness depends on posting all four "
    "families of exactly-one groups and retaining every clue."
)

doc.add_heading("4.4 SAT formulation and variable mapping", level=2)
doc.add_paragraph(
    "Define a Boolean variable x[r,c,v] that is true if cell (r,c) contains "
    "value v. The implementation maps a one-based digit d to a positive "
    "variable identifier with var_id(r,c,d,N)=rN²+cN+d. Thus the primary "
    "variable range is 1 through N³, and any cardinality-encoding auxiliaries "
    "are allocated above that range. The encoding enforces "
    "exactly one value per cell, exactly one occurrence of each value in every "
    "row and column, and exactly one occurrence of each value in each subgrid. "
    "Clues fix the corresponding cell values using positive unit clauses."
)
doc.add_paragraph(
    "An exactly-one constraint over a set X combines an at-least-one constraint "
    "with an at-most-one (AMO) constraint:"
)
doc.add_paragraph("OR(x in X) AND AMO(X).")
doc.add_paragraph(
    "The implementation constructs a positive ALO clause for each group, then "
    "uses the selected PySAT cardinality encoding for AMO. Pairwise has a direct "
    "quadratic clause count and no auxiliary variables. Sequential counter "
    "adds auxiliary state variables to represent partial counts and uses a "
    "linear-size construction. This report treats the resulting runtimes as "
    "measurements of the full SAT wrapper: CNF construction, solver creation, "
    "search, and model decoding are all inside the timed call."
)

doc.add_heading("4.5 CP-SAT and MIP formulations", level=2)
doc.add_paragraph(
    "The CP-SAT solver creates N² integer variables with domain 1..N, posts "
    "all-different constraints for each row, column, and box, and fixes all "
    "clues. The returned status is accepted only for FEASIBLE or OPTIMAL; "
    "infeasible or unknown outcomes produce no grid. The wrapper returns the "
    "values of the integer variables as a nested list [7]."
)
doc.add_paragraph(
    "The CPLEX CP Optimizer adapter uses the same N² integer-domain structure "
    "and all-different groups. Its interface accepts a time_limit argument "
    "with a default of 60 seconds, and it returns a grid only when the solver "
    "reports a solution. The other standard 9×9 wrappers do not expose a "
    "project-level common timeout parameter, so the benchmark should not be "
    "described as applying a uniform explicit cutoff to every solver."
)
doc.add_paragraph(
    "The CPLEX MIP and Gurobi adapters create N³ binary variables and equality "
    "constraints for each cell, row-digit, column-digit, and box-digit group. "
    "Clues are fixed by adding a singleton constraint. The objective is "
    "constant. Both wrappers extract the chosen digit for each cell from the "
    "solver's incumbent values. CPLEX's Python model is explicitly ended in a "
    "finally block, and Gurobi's model is disposed in a finally block, so "
    "solver resources are released on normal return and exceptions."
)

doc.add_heading("5. Software architecture and implementation", level=1)
doc.add_heading("5.1 Module boundaries", level=2)
doc.add_paragraph(
    "The repository separates solver implementations from experiment drivers. "
    "The SAT encoder and solver are in src/sudoku_sat.py; CP-SAT, CPLEX MIP, "
    "CPLEX CP Optimizer, and Gurobi are implemented in their respective "
    "src/sudoku_*.py modules. src/scaled_sudoku.py parses the scaled text format. "
    "The benchmarks directory contains the standard and scaled runners, "
    "dataset validators, AMO comparison, and plotting scripts. Tests exercise "
    "solver behavior and invalid-input handling. The report generator reads "
    "CSV and image outputs from results/ rather than running the experiments "
    "during document creation."
)
doc.add_paragraph(
    "This separation matters for reproducibility: generating the DOCX is a "
    "deterministic transformation of existing artifacts, while running a "
    "benchmark invokes third-party solver libraries and may depend on local "
    "installations or licenses. The report therefore does not silently rerun "
    "a potentially long experiment when a reader asks to rebuild the document."
)

doc.add_heading("5.2 SAT encoding construction", level=2)
doc.add_paragraph(
    "The SAT encoder validates that the input is a non-empty square, checks "
    "that its size is a perfect square, and verifies that every entry is an "
    "integer in the inclusive range 0..N (with zero denoting an empty cell). "
    "Boolean values are explicitly rejected even though Python treats bool "
    "as a subclass of int. It then builds four families of exactly-one groups: "
    "one digit per cell, one occurrence of each digit per row, per column, "
    "and per box. Given clues become unit clauses. The solver is created with "
    "the G3 backend and the generated clauses; an unsatisfiable formula yields "
    "None, while a satisfying model is decoded into an N×N integer grid."
)
doc.add_paragraph(
    "The variable identifier formula is collision-free across cells and "
    "digits: each (row,column) reserves a contiguous block of N identifiers. "
    "Auxiliary variables generated by CardEnc are allocated after the primary "
    "range by carrying forward the encoder's returned variable ceiling. This "
    "prevents a cardinality encoding from reusing an identifier belonging to "
    "a Sudoku decision variable or an earlier auxiliary variable."
)

doc.add_heading("5.3 Scaled puzzle representation", level=2)
doc.add_paragraph(
    "Scaled puzzle files use a header declaring SIZE=N, followed by exactly "
    "N rows of N symbols. The loader ignores blank and comment lines, maps "
    "a period to zero, and maps the symbol string 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ "
    "to integer values. It rejects a missing size header, inconsistent row "
    "dimensions, unknown characters, and symbols whose decoded value exceeds "
    "N. The puzzle content is normalized to uppercase before parsing, so "
    "alphabetic symbols are handled without case sensitivity."
)
doc.add_paragraph(
    "This representation supports the tested 16×16 and 25×25 grids without "
    "changing solver APIs: once loaded, each puzzle is an ordinary nested "
    "integer list. The SAT and CP/MIP solvers still require square box sizes; "
    "the automatic box rule is appropriate for N=q² and does not generalize "
    "to rectangular box dimensions."
)

doc.add_heading("6. Correctness, testing, and measurement", level=1)
doc.add_heading("6.1 Independent solution validation", level=2)
doc.add_paragraph(
    "The benchmark's validity check does not trust the solver status alone. "
    "For a standard board it checks the result dimensions, requires each row "
    "and column to contain exactly the set {1,…,9}, checks every 3×3 box, and "
    "compares all non-zero input clues against the returned values. The scaled "
    "validator applies the same structural test with the range {1,…,N} and "
    "boxes of side √N. A solution is recorded as SOLVED only if the returned "
    "grid passes this validation. An exception is recorded as ERROR with its "
    "message in the scaled CSV."
)
doc.add_paragraph(
    "This validation strategy detects incomplete grids, duplicate values, "
    "broken box constraints, and altered clues even if a solver adapter "
    "incorrectly reports success. It does not independently prove uniqueness, "
    "and a successful validation cannot detect that the input itself was "
    "transcribed incorrectly relative to an external source. Dataset checks "
    "and solver checks address different failure modes and should be reported "
    "separately."
)

doc.add_heading("6.2 Test coverage and invalid inputs", level=2)
doc.add_paragraph(
    "The SAT unit tests include a known 9×9 puzzle, solution-rule checks, "
    "preservation of the clues, contradictory input, malformed grid shapes, "
    "out-of-range and non-integer values, and both supported AMO encodings. "
    "The validation scripts exercise the standard dataset before a benchmark "
    "and the scaled runner validates each generated result. Together these "
    "checks make correctness a precondition of timing rather than a post-hoc "
    "assumption."
)
doc.add_paragraph(
    "The solver APIs intentionally reject malformed shapes and values with "
    "ValueError rather than attempting to repair them. A validly shaped but "
    "contradictory Sudoku is a different case: it is a well-formed constraint "
    "instance with no solution, so the SAT and CP-SAT APIs return None. This "
    "distinction is important when interpreting benchmark statuses: invalid "
    "input is not equivalent to an unsatisfiable puzzle."
)

doc.add_heading("6.3 Timed region and summary statistics", level=2)
doc.add_paragraph(
    "In the standard runner, time.perf_counter() is sampled immediately before "
    "and after the solver function. Model construction, solver invocation, and "
    "solution extraction are therefore included. Dataset reading and the "
    "independent validity check are outside this interval. Each solver receives "
    "one warm-up call for every puzzle; that call is validated but not included "
    "in the five measured repetitions. The CSV stores one median per "
    "puzzle-solver pair."
)
doc.add_paragraph(
    "For a difficulty group, the chart and report's group mean are computed "
    "from the ten per-puzzle medians, not from the fifty individual timed "
    "repetitions. The group median is likewise the median of those ten "
    "per-puzzle medians. This two-stage aggregation reduces sensitivity to a "
    "single repeated-run fluctuation but conceals within-puzzle variance, "
    "which the current CSV does not retain."
)
doc.add_paragraph(
    "The scaled runner makes one timed call per puzzle and solver, with no "
    "warm-up loop and no configured timeout in the benchmark script. The "
    "elapsed field excludes the subsequent solution validation. Thus the "
    "scaled mean and median describe single observations, not repeated-run "
    "distributions; the long tail in the 25×25 results is especially important "
    "when considering their arithmetic means."
)

doc.add_heading("7. Experimental protocol", level=1)
doc.add_heading("7.1 Standard 9×9 dataset", level=2)
add_table(doc, ["Dataset", "Instances", "Purpose"], [
    ["Easy", "10 puzzles", "Standard-grid comparison"],
    ["Medium", "10 puzzles", "Standard-grid comparison"],
    ["Hard", "10 puzzles", "Standard-grid comparison"],
    ["16×16", "10 puzzles", "Scaled-grid comparison"],
    ["25×25", "10 puzzles", "Larger scaled-grid comparison"],
])
doc.add_paragraph(
    "The standard 9x9 instances are stored in data/sudoku_instances.json. "
    "There are 30 puzzles, ten in each labeled group. In the checked dataset, "
    "the easy puzzles contain 46–51 clues (mean 49.1), medium puzzles contain "
    "36–41 clues (mean 38.3), and hard puzzles contain 27–31 clues (mean 29.7). "
    "The labels therefore correspond to clue-count bands in this dataset. "
    "They should not be interpreted as a validated human difficulty scale or "
    "as a guarantee of solver difficulty."
)
doc.add_paragraph(
    "The scaled instances are stored under data/scaled-sudoku-sample/. The "
    "format uses '.' for empty cells and symbols to represent values above 9. "
    "The runner selects the first ten sorted .sdk.txt paths under each size "
    "directory, so its evaluated sample is deterministic with respect to the "
    "repository's directory contents and filename ordering. There are ten "
    "16×16 puzzles and ten 25×25 puzzles. The upstream dataset should be cited "
    "and any changes to the selected files should be disclosed [10]."
)
doc.add_heading("7.1.1 Standard puzzle generation and grouping", level=2)
doc.add_paragraph(
    "The repository includes a deterministic 9×9 dataset-generation script "
    "with a pseudorandom seed of 2026. It creates a complete valid grid from "
    "a Sudoku pattern by shuffling digit labels, row bands and rows within "
    "each band, and column stacks and columns within each stack. It then "
    "removes a randomly selected set of cells. The target empty-cell intervals "
    "in the generator are 30–35 for easy, 40–48 for medium, and 50–55 for "
    "hard. For each candidate puzzle, the script solves once, adds a blocking "
    "clause for that complete assignment, and solves again; a candidate is "
    "accepted only when no second solution exists."
)
doc.add_paragraph(
    "The recorded clues agree with those design bands: 46–51 clues for easy, "
    "36–41 for medium, and 27–31 for hard. The group names are therefore "
    "operational labels derived from the number of removed cells, rather "
    "than claims about logical technique count or human solving time. Random "
    "cell removal can also yield puzzles with different structural patterns "
    "even when their clue counts are similar. The experiment uses the fixed "
    "JSON dataset in the repository, so regenerating it is not necessary to "
    "reproduce the recorded benchmark and could replace the exact inputs."
)

doc.add_heading("7.2 Solver matrix", level=2)
add_table(doc, ["Solver", "Model family", "Role in this evaluation"], [
    ["SAT", "Boolean satisfiability", "Boolean encoding of Sudoku rules"],
    ["CP-SAT", "Constraint programming / SAT hybrid", "Integer constraint model"],
    ["CPLEX MIP", "Mixed-integer programming", "Binary-variable linear model"],
    ["Gurobi", "Mixed-integer programming", "Binary-variable linear model"],
    ["CPLEX CP", "Constraint programming", "Additional solver in the 9x9 comparison"],
])
doc.add_paragraph(
    "The standard CSV contains 30 instances × 5 solvers = 150 records. The "
    "scaled CSV contains 2 grid sizes × 10 puzzles × 4 solvers = 80 records. "
    "CPLEX CP is not included in the scaled comparison. The separate AMO file "
    "contains 30 instances × 2 encodings = 60 records."
)

doc.add_heading("7.3 Repetition, warm-up, and outcome handling", level=2)
doc.add_paragraph(
    "The standard benchmark performs a warm-up for every solver and puzzle, "
    "then five measured runs. The warm-up is not timed into the reported "
    "median, but it can influence process-level caches, library initialization, "
    "and solver startup behavior. The benchmark raises an error if any returned "
    "solution fails validation, so invalid outputs are not silently converted "
    "into apparently successful timing rows. The AMO experiment uses the same "
    "warm-up and five-measurement policy."
)
doc.add_paragraph(
    "The scaled runner stores size, puzzle filename, solver, status, validity, "
    "time_seconds, and any exception text. It proceeds solver by solver, "
    "records ERROR for a caught exception, and continues with other combinations. "
    "The current output has 80 records, each marked SOLVED and valid. This is "
    "evidence about this run only; it does not establish expected failure or "
    "timeout rates for other environments."
)
doc.add_paragraph(
    "The repository's CSV files do not embed a complete machine specification, "
    "Python version, exact solver build, thread count, or all solver parameters. "
    "Those omissions prevent a full independent reproduction of timings from "
    "the CSV alone. Before submission, the author should add the actual machine "
    "and environment information rather than infer it from unrelated examples "
    "or from package requirements."
)

doc.add_heading("8. Empirical findings", level=1)
doc.add_heading("8.1 Experiment A: AMO encoding comparison", level=2)
amo_rows = read_csv(RESULTS / "benchmark_amo.csv")
amo_groups = {}
for row in amo_rows:
    try:
        key = (row["difficulty"].strip().lower(), row["encoding"].strip())
        seconds = float(row["median_time_seconds"])
    except (ValueError, KeyError, AttributeError):
        continue
    if seconds >= 0:
        amo_groups.setdefault(key, []).append(seconds)

if amo_rows:
    amo_summary_rows = []
    for difficulty in ("easy", "medium", "hard"):
        pairwise = amo_groups.get((difficulty, "pairwise"), [])
        seqcounter = amo_groups.get((difficulty, "seqcounter"), [])
        difficulty_wins = 0
        if pairwise and seqcounter:
            pairwise_by_instance = {}
            seqcounter_by_instance = {}
            for row in amo_rows:
                if row.get("difficulty", "").strip().lower() != difficulty:
                    continue
                try:
                    value = float(row["median_time_seconds"])
                    instance = int(row["instance"])
                except (ValueError, KeyError):
                    continue
                target = (
                    pairwise_by_instance
                    if row.get("encoding") == "pairwise"
                    else seqcounter_by_instance
                )
                target[instance] = value
            difficulty_wins = sum(
                seqcounter_by_instance[i] < pairwise_by_instance[i]
                for i in pairwise_by_instance.keys() & seqcounter_by_instance.keys()
            )
            amo_summary_rows.append([
                difficulty.title(),
                str(min(len(pairwise), len(seqcounter))),
                fmt_seconds(statistics.mean(pairwise)),
                fmt_seconds(statistics.mean(seqcounter)),
                fmt_seconds(statistics.median(pairwise)),
                fmt_seconds(statistics.median(seqcounter)),
                f"{difficulty_wins}/10",
            ])
    add_table(
        doc,
        [
            "Group", "Puzzles", "Pairwise mean (s)", "Seq. mean (s)",
            "Pairwise median (s)", "Seq. median (s)", "Seq. faster",
        ],
        amo_summary_rows,
    )
    doc.add_paragraph(
        "Each value is aggregated from puzzle-level medians, with five measured "
        "runs per puzzle and encoding. In the current data, sequential counter "
        "is faster on 8/10 easy, 10/10 medium, and 8/10 hard instances. It has "
        "a lower group mean and median in all three categories. This result "
        "supports a dataset-specific runtime observation; it does not show "
        "that sequential counters dominate pairwise AMO for every puzzle, "
        "solver engine, or hardware configuration."
    )
    add_figure(
        doc,
        RESULTS / "amo_encoding_comparison.png",
        "Figure 1. Recorded AMO encoding comparison. The two encodings use the "
        "same SAT engine and standard puzzle set.",
        width=5.8,
    )
else:
    doc.add_paragraph(
        "The AMO benchmark file was not found. Run benchmarks.benchmark_amo "
        "before reporting encoding-specific conclusions."
    )
doc.add_heading("8.2 Experiment B: five solvers on standard Sudoku", level=2)
rows9 = read_csv(RESULTS / "benchmark_sat_cpsat_cplex_mip_cplex_cp_gurobi.csv")
if rows9:
    groups = {}
    for row in rows9:
        try:
            seconds = float(row["median_time_seconds"])
            difficulty = row["difficulty"].strip().lower()
            solver = row["solver"].strip()
        except (ValueError, KeyError, AttributeError):
            continue
        if seconds >= 0:
            groups.setdefault((difficulty, solver), []).append(seconds)

    difficulties = ["easy", "medium", "hard"]
    solver_order = ["SAT", "CP-SAT", "CPLEX MIP", "CPLEX CP", "Gurobi"]
    available = {solver for _, solver in groups}
    solvers = [solver for solver in solver_order if solver in available]
    solvers += sorted(available - set(solver_order))
    table_rows = []
    for difficulty in difficulties:
        for solver in solvers:
            values = groups.get((difficulty, solver), [])
            if values:
                table_rows.append([
                    difficulty.title(), solver, str(len(values)),
                    fmt_seconds(statistics.mean(values)),
                    fmt_seconds(statistics.median(values)),
                ])
    add_table(doc, ["Difficulty", "Solver", "Instances", "Mean (s)", "Median (s)"], table_rows)
    doc.add_paragraph(
        "Table values are calculated from the per-instance median times in the "
        "current benchmark CSV. For each group, the mean is the arithmetic mean "
        "of the instance-level medians; the median is the median of those values. "
        "Values are rounded to four decimal places."
    )
else:
    doc.add_paragraph("The 9x9 benchmark CSV was not found. Run the benchmark before using this report.")

add_figure(
    doc,
    RESULTS / "sat_vs_cpsat_cplex_gurobi.png",
    "Figure 2. Five-solver comparison on 30 standard 9×9 Sudoku instances. "
    "Bars show the mean of per-instance median solving times for each "
    "clue-count group.",
    width=5.8,
)

doc.add_heading("8.2.1 Standard benchmark interpretation", level=2)
doc.add_paragraph(
    "In this run, CPLEX MIP has the lowest group mean and median among the five "
    "tested solvers in easy, medium, and hard groups. SAT is generally the next "
    "fastest in these summary statistics, while CP-SAT and Gurobi are close to "
    "one another and CPLEX CP is slower on these particular 9×9 instances. "
    "The absolute differences are measured in milliseconds, so fixed Python "
    "and solver setup costs are a material part of the timed call. These are "
    "observations about the current wrappers and dataset, not a claim that one "
    "solver technology is universally faster."
)
doc.add_paragraph(
    "The CSV records 150 puzzle-solver medians, with ten records per solver in "
    "each difficulty group. Across the groups, the medians are stable in scale: "
    "all five solvers complete the measured 9×9 calls in roughly hundredths of "
    "a second. The category ordering should be treated cautiously because "
    "difficulty was assigned using clue counts, and not all solver work is "
    "strictly proportional to the number of clues."
)

doc.add_heading("8.3 Experiment C: scaled 16×16 and 25×25 Sudoku", level=2)
scaled = read_csv(RESULTS / "benchmark_scaled_all_solvers.csv")
valid_rows = []
for row in scaled:
    try:
        valid = row.get("valid", "").strip().lower() == "true"
        solved = row.get("status", "").strip().upper() == "SOLVED"
        seconds = float(row["time_seconds"])
        size = int(row["size"])
        solver = row["solver"].strip()
    except (ValueError, KeyError, AttributeError):
        continue
    if valid and solved and seconds >= 0:
        valid_rows.append({"size": size, "solver": solver, "seconds": seconds})

if valid_rows:
    table_rows = []
    preferred_order = ["SAT", "CP-SAT", "CPLEX MIP", "Gurobi"]
    for size in sorted({record["size"] for record in valid_rows}):
        available_solvers = sorted({
            record["solver"] for record in valid_rows if record["size"] == size
        })
        ordered_solvers = [s for s in preferred_order if s in available_solvers]
        ordered_solvers += [s for s in available_solvers if s not in preferred_order]
        for solver in ordered_solvers:
            values = [
                record["seconds"] for record in valid_rows
                if record["size"] == size and record["solver"] == solver
            ]
            table_rows.append([
                f"{size}x{size}", solver, str(len(values)),
                fmt_seconds(statistics.mean(values)),
                fmt_seconds(statistics.median(values)),
                fmt_seconds(min(values)),
                fmt_seconds(max(values)),
            ])
    add_table(
        doc,
        ["Grid", "Solver", "Valid", "Mean (s)", "Median (s)", "Min (s)", "Max (s)"],
        table_rows,
    )
else:
    doc.add_paragraph("No valid solved records were found in the scaled benchmark CSV. Run and validate the benchmark before submission.")

add_figure(
    doc,
    RESULTS / "scaled_sudoku_16x16_comparison.png",
    "Figure 3. Mean runtime comparison for the tested 16×16 Sudoku instances. "
    "Only solved and valid benchmark records are included.",
    width=5.8,
)
add_figure(
    doc,
    RESULTS / "scaled_sudoku_25x25_comparison.png",
    "Figure 4. Mean runtime comparison for the tested 25×25 Sudoku instances. "
    "Only solved and valid benchmark records are included.",
    width=5.8,
)

doc.add_heading("8.4 Interpretation of the scaled results", level=2)
doc.add_paragraph(
    "For 16×16, CPLEX MIP has the smallest mean and median in the recorded set "
    "(about 0.082 s mean and 0.053 s median), while SAT and CP-SAT have means "
    "of about 0.114 s and 0.119 s. Gurobi has a higher mean than median because "
    "one or more puzzles take substantially longer than the central instance. "
    "The measured 16×16 values remain below one second for all solvers in this "
    "run, but the order is specific to the chosen ten inputs."
)
doc.add_paragraph(
    "At 25×25, the arithmetic means expose a pronounced runtime tail: SAT "
    "averages about 4.99 s, CP-SAT 5.58 s, CPLEX MIP 59.69 s, and Gurobi "
    "457.00 s. The corresponding medians are approximately 4.13 s, 3.19 s, "
    "25.97 s, and 133.13 s. CP-SAT has the lowest median, while SAT has the "
    "lowest mean. The maximum recorded Gurobi call exceeds 3,300 s, and the "
    "maximum CPLEX MIP call is about 280 s. Reporting only the mean or only "
    "the median would hide this difference in tail behavior; both statistics "
    "are therefore shown, and the 25×25 chart should be read on its plotted "
    "linear scale with the underlying table in view."
)
doc.add_paragraph(
    "All 80 scaled records were marked SOLVED and valid, but the runner does "
    "not enforce a timeout. Thus 'all solved' describes eventual observed "
    "outcomes, not completion within a fixed operational budget. The results "
    "show that scaling from 16×16 to 25×25 increases measured effort sharply "
    "for some solver-instance pairs; they do not establish a general complexity "
    "curve from only two sizes."
)

doc.add_heading("9. Discussion", level=1)
doc.add_heading("9.1 Encoding size is not runtime", level=2)
doc.add_paragraph(
    "The AMO results point to a consistent but modest advantage for sequential "
    "counter on this standard dataset: it wins 26 of 30 puzzle-level comparisons, "
    "and has lower group means and medians in all three labels. This is a useful "
    "within-engine observation because the same SAT implementation is called "
    "with only the AMO encoding changed. It does not establish that the smaller "
    "asymptotic clause growth is the sole reason for the measured difference; "
    "the current CSV has no clause counts, auxiliary-variable counts, solver "
    "statistics, or repeated-run distributions for each puzzle."
)
doc.add_paragraph(
    "The five-solver 9×9 experiment answers a different question. It compares "
    "complete solver calls rather than holding the backend constant while "
    "changing one SAT encoding. CPLEX MIP's low recorded times may reflect its "
    "model, API overhead, presolve, and solver implementation together. Since "
    "the measurement window includes construction and solution extraction, "
    "the table cannot be interpreted as a pure comparison of search algorithms."
)

doc.add_heading("9.2 Scaling and distribution shape", level=2)
doc.add_paragraph(
    "The scaled results illustrate why both mean and median are informative. "
    "For the 25×25 puzzles, means substantially exceed medians for CPLEX MIP "
    "and especially Gurobi, showing that a small number of very long calls "
    "raise the average. The runner retains the individual times, so the "
    "reported minimum and maximum make this spread visible. Because there "
    "are only ten instances and no repeated runs, these statistics are "
    "descriptive summaries rather than estimates of a stable population "
    "distribution."
)
doc.add_paragraph(
    "The number of decision variables also grows differently across model "
    "families. A direct Boolean SAT or MIP representation has N³ candidate "
    "indicators before encoding auxiliaries; an integer-domain CP model has "
    "N² cell variables but more complex global constraints. Variable counts "
    "alone do not predict runtime: propagation strength, encoding structure, "
    "presolve, branching, and the tested clue pattern all matter. A stronger "
    "scaling study would include more grid sizes, more instances at every size, "
    "and model-specific resource statistics."
)

doc.add_heading("9.3 Practical reproducibility", level=2)
doc.add_paragraph(
    "The standard benchmark's five repetitions and medians offer more "
    "protection against transient timing noise than the one-shot scaled "
    "measurements. The warm-up also reduces the impact of first-use library "
    "initialization in measured runs, although it is still part of the "
    "experimental protocol and should be held constant when reproducing the "
    "results. Solver defaults and parameter settings should be captured "
    "alongside package versions, since defaults may change across releases."
)
doc.add_paragraph(
    "A reproducible rerun should preserve the exact input files, execute the "
    "same scripts from the repository root, retain raw CSV output, and record "
    "the operating system, CPU, memory, Python version, solver versions, "
    "thread settings, and license type. A benchmark run should not overwrite "
    "an earlier result without archiving it; otherwise, a report generated "
    "later may no longer correspond to the dataset summarized here."
)
doc.add_heading("9.4 Interpreting a solver call as a system measurement", level=2)
doc.add_paragraph(
    "A Python-level call can include costs that are small on a hard instance "
    "but prominent on an easy one: importing or initializing a solver backend, "
    "allocating variables, constructing constraints, transferring the model "
    "to the native engine, retrieving a solution, and translating it into "
    "Python lists. The benchmark starts its timer after imports and input "
    "loading, but the solver functions build a fresh model for every invocation. "
    "As a result, the recorded time does not include module import or dataset "
    "parsing, but does include per-call formulation work and extraction."
)
doc.add_paragraph(
    "This boundary is appropriate when the practical question is how long "
    "the repository's solver API takes to solve one supplied puzzle. A study "
    "focused on search-engine efficiency would need a different protocol: "
    "separate model-build and solve timers, disclose presolve and search "
    "settings, and possibly count conflicts, branches, propagations, or "
    "memory. The present CSVs do not provide these internal counters, so the "
    "report does not attempt to attribute observed time differences to one "
    "specific internal algorithm."
)

doc.add_heading("10. Threats to validity and limitations", level=1)
for item in [
    "Sample size: the standard comparison has 30 puzzles and each scaled size has ten. A few instances cannot characterize the full diversity of Sudoku.",
    "Difficulty labels: easy, medium, and hard correspond to groups with different clue counts in this dataset, not to an independently validated difficulty measure.",
    "Hardware and environment: the CSVs do not record a complete machine and software inventory. The absolute times are not portable without that information.",
    "Solver configuration: solver versions, thread counts, and all relevant parameter defaults are not embedded in the result files; comparisons may change across releases.",
    "Different model families: the comparison is system-level. SAT, CP-SAT, CP, and MIP use different representations and internal procedures.",
    "Unequal repeated measurements: standard runs have five repetitions after warm-up; scaled runs are single measurements. Variability is therefore characterized unevenly.",
    "No scaled timeout: the scaled runner does not set a common time limit. A successful status does not mean completion under a fixed service-level budget.",
    "External validity: results apply to the selected puzzles, code versions, and local environment; they do not prove universal solver rankings or asymptotic behavior.",
    "Uniqueness: the solution validators check feasibility and clue preservation, not uniqueness. A puzzle's single reported solution is not proof that no other solution exists.",
    "Timing scope: model construction and decoding are included, while file I/O and independent validation are excluded. Another timing boundary could yield different rankings.",
    "Potential environment noise: background processes, power management, thermal throttling, and solver licensing can affect wall-clock measurements.",
]:
    add_bullet(doc, item)

doc.add_heading("11. Conclusion and future work", level=1)
doc.add_paragraph(
    "This study documents a Sudoku-solving project that spans SAT, CP-SAT, "
    "CPLEX CP, and two MIP implementations, and reports three complementary "
    "measurement sets: pairwise versus sequential-counter AMO on standard "
    "puzzles; five solver implementations on 9×9 Sudoku; and four solvers on "
    "16×16 and 25×25 puzzles. The current standard CSV shows CPLEX MIP with "
    "the lowest group-level mean and median in each difficulty category. The "
    "AMO CSV favors sequential counter on 26 of 30 instances. In the scaled "
    "set, CPLEX MIP has the lowest 16×16 mean and median; at 25×25, SAT has "
    "the lowest mean while CP-SAT has the lowest median. These metric-dependent "
    "observations reinforce that rankings depend on size, sample, and summary "
    "statistic."
)
doc.add_paragraph(
    "Several extensions would strengthen the evidence. First, repeat the "
    "scaled runs under a fixed and documented timeout, with multiple runs per "
    "puzzle and explicit reporting of censoring, errors, and failures. Second, "
    "record environment and solver metadata in each result row. Third, collect "
    "build time, solve time, variable and constraint counts, memory use, and "
    "solver statistics so that runtime differences can be analyzed rather "
    "than merely ranked. Fourth, expand the puzzle sample and use a documented "
    "difficulty or source-selection procedure. Finally, extend the AMO study "
    "only after implementing the additional encodings and validating them "
    "against the same independent correctness checks."
)

doc.add_heading("12. Data availability", level=1)
doc.add_paragraph(
    "Source code, test files, datasets, result CSVs, and figure scripts are "
    "maintained in the project repository [11]:"
)
add_code_line(doc, "https://github.com/transonnn/sudoku-sat-solver")
doc.add_paragraph(
    "The principal artifacts used by this manuscript are "
    "data/sudoku_instances.json; data/scaled-sudoku-sample/; "
    "results/benchmark_amo.csv; "
    "results/benchmark_sat_cpsat_cplex_mip_cplex_cp_gurobi.csv; "
    "results/benchmark_scaled_all_solvers.csv; and the figures in results/. "
    "The report can be regenerated from the repository root after installing "
    "the Python packages required by report/generate_report.py. Solver "
    "benchmarks additionally require their corresponding solver packages "
    "and licenses."
)

doc.add_heading("References", level=1)
references = [
    "Biere, A., Heule, M., van Maaren, H., and Walsh, T. (eds.). Handbook of Satisfiability, 2nd ed. IOS Press, 2021.",
    "Knuth, D. E. Dancing links. In: Millennial Perspectives in Computer Science, 2000, pp. 187–214.",
    "Sinz, C. Towards an optimal CNF encoding of Boolean cardinality constraints. In: Principles and Practice of Constraint Programming, 2005, pp. 827–831.",
    "Eén, N. and Sörensson, N. An extensible SAT-solver. In: Theory and Applications of Satisfiability Testing, 2003, pp. 502–518.",
    "Ignatiev, A., Morgado, A., and Marques-Silva, J. PySAT: A Python toolkit for prototyping with SAT oracles. In: SAT, 2018, pp. 428–437.",
    "Régin, J.-C. A filtering algorithm for constraints of difference in CSPs. In: AAAI, 1994, pp. 362–367.",
    "Google OR-Tools. CP-SAT Solver documentation. https://developers.google.com/optimization/cp/cp_solver",
    "IBM. IBM ILOG CPLEX Optimization Studio documentation. https://www.ibm.com/docs/en/icos",
    "Gurobi Optimization. Gurobi Optimizer documentation. https://docs.gurobi.com/",
    "Scaled Sudoku Instances. Dataset repository. https://github.com/zayenz/scaled-sudoku-instances",
    "Sudoku SAT Solver. Source code and experimental artifacts. https://github.com/transonnn/sudoku-sat-solver",
]
for reference in references:
    doc.add_paragraph(reference, style="List Number")

doc.add_heading("Appendix A. Reproducing the experiments", level=1)
doc.add_paragraph(
    "Run commands from the repository root after activating the project virtual "
    "environment. Solver-specific dependencies and license configuration must "
    "be available for the corresponding solver."
)
for command in [
    "python -m pytest -v",
    "python -u benchmarks/validate_datasets.py",
    "python -u benchmarks/benchmark_amo.py",
    "python -m benchmarks.benchmark",
    "python -m benchmarks.benchmark_scaled_solvers",
    "python -m benchmarks.plot_results",
    "python -m benchmarks.plot_scaled_results",
    "python -u report/generate_report.py",
]:
    add_code_line(doc, command)
doc.add_paragraph(
    "Commands that invoke all commercial solvers may require local installations "
    "and active licenses. Do not run a fresh benchmark merely to regenerate this "
    "document if the existing CSVs are the intended evidence; the report script "
    "reads the stored results and plots. Before submission, confirm that the "
    "author name and corresponding email are correct; add institutional "
    "affiliation, course, or date details only if they are required. Record "
    "the actual computer, operating system, Python and solver versions, license "
    "types, and relevant parameters. Review page breaks, table widths, figure "
    "captions, and references in Microsoft Word."
)

doc.add_heading("Appendix B. Reading the result tables", level=1)
doc.add_paragraph(
    "In the standard table, N is fixed at 9 and each row summarizes one "
    "difficulty-solver group. 'Instances' is the number of puzzle-level "
    "medians included, normally ten. The mean and median are calculated in "
    "seconds and rounded for display; the underlying CSV stores higher "
    "precision. The AMO table follows the same aggregation but compares "
    "encodings rather than solver names."
)
doc.add_paragraph(
    "In the scaled table, 'Valid' is the count of records included after "
    "requiring status SOLVED, valid=True, and a non-negative elapsed time. "
    "Mean, median, minimum, and maximum are computed over those individual "
    "records. The scaled benchmark records one observation per puzzle-solver "
    "pair, so these columns describe the finite sample and should not be "
    "mistaken for repeated-trial confidence intervals."
)

doc.add_heading("Appendix C. Notation and terminology", level=1)
add_table(doc, ["Term", "Meaning in this report"], [
    ["N", "Number of rows, columns, and symbols in an N×N Sudoku grid."],
    ["q", "Side length of a square subgrid; N=q²."],
    ["AMO", "At-most-one constraint over a set of Boolean literals."],
    ["ALO", "At-least-one clause requiring at least one candidate literal to be true."],
    ["Exactly-one", "Conjunction of ALO and AMO constraints."],
    ["CNF", "Conjunctive normal form: a conjunction of disjunctive clauses."],
    ["MIP", "Mixed-integer programming; here, a binary feasibility model."],
    ["CP", "Constraint programming over finite-domain variables and global constraints."],
    ["Per-puzzle median", "Median of five measured calls for one standard puzzle and solver."],
    ["Group mean", "Arithmetic mean of the puzzle-level medians within a category."],
])

doc.add_heading("Appendix D. Data and result-file inventory", level=1)
add_table(doc, ["Artifact", "Role", "Reported observations"], [
    ["data/sudoku_instances.json", "Standard 9×9 clue grids grouped by label", "30 puzzles"],
    ["data/scaled-sudoku-sample/", "Scaled Sudoku text puzzles", "10 puzzles per size"],
    ["results/benchmark_amo.csv", "Pairwise and sequential-counter timings", "60 puzzle-encoding medians"],
    ["results/benchmark_sat_cpsat_cplex_mip_cplex_cp_gurobi.csv", "Five-solver standard benchmark", "150 puzzle-solver medians"],
    ["results/benchmark_scaled_all_solvers.csv", "Scaled solver outcomes and elapsed calls", "80 puzzle-solver calls"],
    ["results/amo_encoding_comparison.png", "AMO timing chart", "Generated from the AMO CSV"],
    ["results/sat_vs_cpsat_cplex_gurobi.png", "Standard five-solver chart", "Mean of puzzle-level medians"],
    ["results/scaled_sudoku_16x16_comparison.png", "16×16 scaled chart", "Mean of valid solved calls"],
    ["results/scaled_sudoku_25x25_comparison.png", "25×25 scaled chart", "Mean of valid solved calls"],
])
doc.add_paragraph(
    "The CSV schemas differ intentionally. Standard benchmark files store the "
    "difficulty label, one-based puzzle index, solver name, repetition count, "
    "and median_time_seconds. The AMO file substitutes an encoding name for "
    "the solver. The scaled file stores grid size, puzzle filename, solver, "
    "status, validity, time_seconds, and error text. When regenerating figures "
    "or this report, use the matching schema and verify that no duplicate or "
    "missing puzzle-solver combinations were introduced."
)

doc.add_page_break()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Inches(2.0)
p.paragraph_format.space_after = Pt(14)
r = p.add_run("PROJECT REPOSITORY")
r.bold = True
r.font.name = "Times New Roman"
r.font.size = Pt(18)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(18)
p.add_run(
    "Source code, datasets, benchmark results, figures, and report generator"
)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(12)
add_hyperlink(
    p,
    "https://github.com/transonnn/sudoku-sat-solver",
    "https://github.com/transonnn/sudoku-sat-solver",
    font_size=14,
)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Click the link above to open the GitHub repository.")

for section in doc.sections:
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("Sudoku Solver Comparative Study | Page ")
    add_word_field(footer, "PAGE")

doc.save(OUTPUT)
print(f"Report created: {OUTPUT}")
print(f"9x9 benchmark records: {len(rows9)}")
print(f"Scaled benchmark records: {len(scaled)}")
print(f"Valid solved scaled records included: {len(valid_rows)}")
