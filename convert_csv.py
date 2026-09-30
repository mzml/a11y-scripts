from __future__ import annotations

import csv
import io
from pathlib import Path

METADATA_PREFIXES = (
    "Created:",
    "Site:",
    "Number of issues:",
    "Expanded column:",
)

BASE_HEADER = [
    "Document title",
    "URL",
    "Document Report",
    "Last modified",
    "Machine-readable",
    "PDF Tags",
    "Issues",
    "Referring pages",
    "Tags",
    "PDF views (30 days)",
]

ISSUE_HEADER = [
    "Issue",
    "Why is this an issue?",
    "How to fix it:",
    "Number of issues",
]


def flatten_siteimprove_export(input_path: Path, output_path: Path) -> None:
    """Convert the UTF-16, tab-delimited export into a clean CSV.

    The source file includes report metadata and repeated issue-detail rows beneath
    each document record. This function removes those metadata rows and emits one
    output row per issue while keeping the parent document fields on each row.
    """
    text = input_path.read_bytes().decode("utf-16")
    rows = list(csv.reader(io.StringIO(text), delimiter="\t", quotechar='"'))

    cleaned_rows = [BASE_HEADER + ISSUE_HEADER]
    current_document: list[str] | None = None
    issue_rows: list[list[str]] = []

    def flush_document() -> None:
        nonlocal current_document, issue_rows

        if current_document is None:
            return

        if issue_rows:
            for issue in issue_rows:
                cleaned_rows.append(current_document + issue)
        else:
            cleaned_rows.append(current_document + [""] * len(ISSUE_HEADER))

        current_document = None
        issue_rows = []

    for row in rows:
        if not row or not any(cell.strip() for cell in row):
            continue

        if row[0].startswith(METADATA_PREFIXES):
            continue

        if row[:10] == BASE_HEADER:
            continue

        if len(row) == 10 and row[0].strip():
            flush_document()
            current_document = row[:10]
            continue

        if len(row) == 14 and row[10].strip() and row[10] != "Issue":
            issue_rows.append(row[10:14])
            continue

    flush_document()

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(cleaned_rows)


def main() -> None:
    input_file = Path("Front Range Community College-Improve PDF accessibility-Table.csv")
    output_file = input_file.with_name(f"{input_file.stem}_fixed.csv")
    flatten_siteimprove_export(input_file, output_file)
    print(f"Converted {input_file.name} -> {output_file.name}")


if __name__ == "__main__":
    main()
