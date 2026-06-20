"""
Policy Document Chunker
=======================
Chunks markdown policy documents by heading (## or ###) rather than
splitting blindly every N characters. This preserves semantic boundaries
and makes retrieval much more useful — a retrieved chunk corresponds to
a complete policy section rather than a random slice of text.

Strategy:
1. Split on ##-level headings (major sections)
2. If a section is > 1000 chars, further split by ### and/or paragraphs
3. Each chunk retains its document name and section heading as metadata
"""

import re
import os
from typing import List, Dict


def chunk_markdown_policy(file_path: str) -> List[Dict[str, str]]:
    """Read a markdown file and split it into semantically meaningful chunks.

    Returns a list of dicts with keys: chunk_id, document_name, section_heading, content
    """
    with open(file_path, "r") as f:
        text = f.read()

    document_name = os.path.splitext(os.path.basename(file_path))[0]

    chunks = []
    # Split on ## headings (major sections)
    sections = re.split(r"\n(?=##\s)", text)

    for sec_idx, section in enumerate(sections):
        lines = section.strip().split("\n")
        heading = ""
        content_lines = []

        for line in lines:
            if line.startswith("## ") or line.startswith("# "):
                heading = line.strip("# ")
            else:
                content_lines.append(line)

        content = "\n".join(content_lines).strip()
        if not content:
            continue

        # If content is too long, split by ### or paragraphs
        if len(content) > 1000:
            sub_sections = re.split(r"\n(?=###\s)", content)
            for sub_idx, sub in enumerate(sub_sections):
                sub = sub.strip()
                if not sub:
                    continue
                sub_heading = heading
                sub_lines = sub.split("\n")
                if sub_lines[0].startswith("### "):
                    sub_heading = f"{heading} > {sub_lines[0].strip('# ')}"
                    sub = "\n".join(sub_lines[1:]).strip()

                chunk_id = f"{document_name}_{sec_idx}_{sub_idx}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "document_name": document_name,
                    "section_heading": sub_heading or document_name,
                    "content": sub,
                })
        else:
            chunk_id = f"{document_name}_{sec_idx}"
            chunks.append({
                "chunk_id": chunk_id,
                "document_name": document_name,
                "section_heading": heading or document_name,
                "content": content,
            })

    return chunks


def chunk_all_policies(policies_dir: str) -> List[Dict[str, str]]:
    """Chunk all markdown files in the policies directory."""
    all_chunks = []
    for fname in sorted(os.listdir(policies_dir)):
        if fname.endswith(".md"):
            fpath = os.path.join(policies_dir, fname)
            chunks = chunk_markdown_policy(fpath)
            all_chunks.extend(chunks)
    return all_chunks
