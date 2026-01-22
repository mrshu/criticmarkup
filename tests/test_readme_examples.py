from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests._helpers import convert_core, normalize_newlines


def _extract_fenced_block(text: str, start_at: int) -> tuple[str, int]:
    fence_re = re.compile(r"```(?P<lang>[^\n]*)\n", re.MULTILINE)
    m = fence_re.search(text, start_at)
    if not m:
        raise AssertionError("Missing fenced code block.")
    lang = m.group("lang").strip()
    end = text.find("\n```", m.end())
    if end == -1:
        raise AssertionError(f"Unclosed fenced code block (lang={lang!r}).")
    content = text[m.end() : end]
    return content, end + len("\n```")


def _extract_example(readme: str, heading: str) -> tuple[str, str]:
    # Find "### <heading>" and then the first "#### Input" + "#### Output" fences beneath it.
    heading_re = re.compile(rf"^###\s+{re.escape(heading)}\s*$", re.MULTILINE)
    m = heading_re.search(readme)
    if not m:
        raise AssertionError(f"Missing README heading: {heading!r}")

    section_start = m.end()
    next_heading = re.compile(r"^###\s+", re.MULTILINE).search(readme, section_start)
    section_end = next_heading.start() if next_heading else len(readme)
    section = readme[section_start:section_end]

    input_marker = re.search(r"^####\s+Input\s*$", section, re.MULTILINE)
    if not input_marker:
        raise AssertionError(f"Missing '#### Input' marker in {heading!r} section.")
    input_text, pos = _extract_fenced_block(section, input_marker.end())

    output_marker = re.search(r"^####\s+Output\s*$", section[pos:], re.MULTILINE)
    if not output_marker:
        raise AssertionError(f"Missing '#### Output' marker in {heading!r} section.")
    output_text, _ = _extract_fenced_block(section, pos + output_marker.end())

    return input_text, output_text


@pytest.mark.parametrize(
    ("heading", "format_name"),
    [
        ("Markdown", "markdown"),
        ("AsciiDoc", "asciidoc"),
        ("LaTeX", "latex"),
    ],
)
def test_readme_examples_match_actual_output(heading: str, format_name: str) -> None:
    readme = normalize_newlines(Path("README.md").read_text(encoding="utf-8"))
    input_text, expected_output = _extract_example(readme, heading)

    actual = convert_core(format_name, normalize_newlines(input_text))
    expected = normalize_newlines(expected_output)

    assert actual.rstrip("\n") == expected.rstrip("\n")
