#!/usr/bin/env python3
"""
Purpose: Validate that a skill directory follows the Skill Authoring Guide.

Checks:
  - SKILL.md exists at the skill directory root.
  - SKILL.md starts with YAML frontmatter containing non-empty `name` and
    `description` fields.
  - `name` matches the frontmatter dir-name convention (lowercase, digits,
    hyphens) and equals the directory name (warning if it differs).
  - `description` is specific and triggerable: reasonably long and includes
    "when to use" wording (e.g. "use when", "use this", "use for").
  - The SKILL.md body (after frontmatter) is under 500 lines.
  - No placeholders from the bundled template remain.
  - A Workflow section includes a concrete validation command and a bounded
    fix-and-rerun loop.
  - examples.md contains 2-4 eval prompts, including a positive and near-miss.
  - Relative markdown links and referenced script/template paths resolve.

Usage:
    python3 scripts/validate_skill.py <path/to/skill-dir>

Exit behavior:
    0  all checks pass (warnings allowed)
    1  one or more errors found
    2  bad invocation (missing/invalid argument)

Requirements: python3 and PyYAML (`python3 -m pip install PyYAML`).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # Report a concise setup error from main().
    yaml = None

MAX_BODY_LINES = 500
MIN_DESC_LEN = 60
USE_WHEN_PAT = re.compile(r"\buse (when|this|for|it when)\b", re.IGNORECASE)
NAME_PAT = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PAT = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
WORKFLOW_HEADING_PAT = re.compile(r"^#{1,6}\s+workflow\b", re.IGNORECASE | re.MULTILINE)
VALIDATION_WORD_PAT = re.compile(r"\b(validat(?:e|ion|or)|tests?|lint(?:er)?)\b", re.IGNORECASE)
INLINE_CODE_PAT = re.compile(r"`([^`\n]+)`")
COMMAND_NAME_PAT = re.compile(
    r"^(python3?|pytest|tox|nox|ruff|mypy|pyright|go|cargo|npm|pnpm|yarn|make|just|bash|sh)\b"
)
REPAIR_PAT = re.compile(r"\b(fix|repair)\w*\b", re.IGNORECASE)
RERUN_PAT = re.compile(r"\bre[- ]?run\w*\b", re.IGNORECASE)
RERUN_LIMIT_PAT = re.compile(
    r"\b(?:2|3|two|three)(?:\s*-\s*(?:2|3|two|three))?\s+"
    r"(?:re[- ]?runs?|attempts?|tries|retries|times?)\b",
    re.IGNORECASE,
)
EVAL_START_PAT = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?:eval prompts?|example test prompts?)\b",
    re.IGNORECASE,
)
HEADING_PAT = re.compile(r"^(#{1,6})\s+")
PROMPT_BULLET_PAT = re.compile(r"^\s*[-*]\s+\S")
TEMPLATE_PLACEHOLDERS = (
    "<skill-name>",
    "<What this does and when to use it. Include likely trigger wording.>",
    "<Skill title>",
    "<path/to/file>",
    "<path/to/test>",
    "<command or script>",
    "<validator command>",
    "scripts/<name>",
    "templates/<name>",
)


def parse_frontmatter(text: str):
    """Return (fields, body_lines, error) after safely parsing YAML."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None, lines, "SKILL.md is missing YAML frontmatter (--- ... ---)."

    closing_index = next(
        (index for index in range(1, len(lines)) if lines[index] == "---"),
        None,
    )
    if closing_index is None:
        return None, lines, "SKILL.md has unterminated YAML frontmatter."

    body = lines[closing_index + 1:]
    try:
        fields = yaml.safe_load("\n".join(lines[1:closing_index]))
    except yaml.YAMLError as exc:
        detail = getattr(exc, "problem", None) or str(exc).splitlines()[0]
        return None, body, f"SKILL.md has invalid YAML frontmatter: {detail}."

    if not isinstance(fields, dict):
        return None, body, "SKILL.md YAML frontmatter must be a mapping."
    return fields, body, None


def _has_validation_command(body_lines):
    """Return whether a command appears near a validation instruction."""
    for index, line in enumerate(body_lines):
        if not VALIDATION_WORD_PAT.search(line):
            continue
        window = "\n".join(body_lines[index:index + 4])
        for candidate in INLINE_CODE_PAT.findall(window):
            candidate = candidate.strip()
            if " " in candidate or "/" in candidate or COMMAND_NAME_PAT.match(candidate):
                return True
    return False


def _find_eval_section(text):
    """Return lines from the first eval-prompt section, or None."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not EVAL_START_PAT.match(line):
            continue
        heading = HEADING_PAT.match(line)
        level = len(heading.group(1)) if heading else None
        end = len(lines)
        for next_index in range(index + 1, len(lines)):
            next_heading = HEADING_PAT.match(lines[next_index])
            if next_heading and (level is None or len(next_heading.group(1)) <= level):
                end = next_index
                break
        return lines[index + 1:end]
    return None


def _validate_completion_gate(skill_dir, body_lines):
    """Return errors for objective workflow and eval requirements."""
    errors = []
    body_text = "\n".join(body_lines)

    placeholders = [item for item in TEMPLATE_PLACEHOLDERS if item in body_text]
    if placeholders:
        errors.append(
            "SKILL.md contains unresolved template placeholder(s): "
            + ", ".join(repr(item) for item in placeholders)
            + "."
        )

    if not WORKFLOW_HEADING_PAT.search(body_text):
        errors.append("SKILL.md is missing a `Workflow` section.")

    if not _has_validation_command(body_lines):
        errors.append(
            "Workflow is missing a concrete validator/test/linter command in backticks."
        )

    if not (REPAIR_PAT.search(body_text) and RERUN_PAT.search(body_text)):
        errors.append("Workflow is missing an explicit fix-and-rerun loop.")
    if not RERUN_LIMIT_PAT.search(body_text):
        errors.append("Workflow is missing a 2-3 attempt/rerun limit.")

    examples_path = skill_dir / "examples.md"
    if not examples_path.is_file():
        errors.append("Missing examples.md with 2-4 eval prompts.")
        return errors

    examples_text = examples_path.read_text(encoding="utf-8")
    eval_lines = _find_eval_section(examples_text)
    if eval_lines is None:
        errors.append("examples.md is missing an eval-prompt section.")
        return errors

    prompts = [line for line in eval_lines if PROMPT_BULLET_PAT.match(line)]
    if not 2 <= len(prompts) <= 4:
        errors.append(
            f"Eval section contains {len(prompts)} prompt(s); expected 2-4."
        )

    eval_text = "\n".join(eval_lines)
    if not re.search(r"^\s*(?:#{1,6}\s*)?positive\b", eval_text, re.IGNORECASE | re.MULTILINE):
        errors.append("Eval section is missing a positive trigger case.")
    if not re.search(
        r"^\s*(?:#{1,6}\s*)?(?:near[- ]miss|out[- ]of[- ]scope)\b",
        eval_text,
        re.IGNORECASE | re.MULTILINE,
    ):
        errors.append("Eval section is missing a near-miss/out-of-scope case.")

    return errors


def main(argv):
    if len(argv) != 2:
        print("usage: validate_skill.py <path/to/skill-dir>", file=sys.stderr)
        return 2
    if yaml is None:
        print(
            "error: PyYAML is required; install it with "
            "`python3 -m pip install PyYAML`.",
            file=sys.stderr,
        )
        return 2

    skill_dir = Path(argv[1]).resolve()
    if not skill_dir.is_dir():
        print(f"error: not a directory: {skill_dir}", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        print(f"error: missing SKILL.md in {skill_dir}", file=sys.stderr)
        return 1

    text = skill_md.read_text(encoding="utf-8")
    if not text.strip():
        errors.append("SKILL.md is empty.")
        _report(errors, warnings)
        return 1

    fm, body, frontmatter_error = parse_frontmatter(text)

    if frontmatter_error:
        errors.append(frontmatter_error)
    else:
        name = fm.get("name")
        desc = fm.get("description")

        if not isinstance(name, str) or not name.strip():
            errors.append("Frontmatter `name` must be a non-empty string.")
        else:
            name = name.strip()
            if not NAME_PAT.match(name):
                errors.append(
                    f"`name` should be lowercase words separated by hyphens: got {name!r}."
                )
            if name != skill_dir.name:
                warnings.append(
                    f"`name` ({name!r}) does not match directory name ({skill_dir.name!r})."
                )

        if not isinstance(desc, str) or not desc.strip():
            errors.append("Frontmatter `description` must be a non-empty string.")
        else:
            desc = desc.strip()
            if len(desc) < MIN_DESC_LEN:
                errors.append(
                    f"`description` is too short ({len(desc)} chars); "
                    f"state what it does AND when to use it (>= {MIN_DESC_LEN} chars)."
                )
            if not USE_WHEN_PAT.search(desc):
                warnings.append(
                    "`description` has no explicit 'use when'/'use for' trigger wording."
                )

    if len(body) > MAX_BODY_LINES:
        errors.append(
            f"SKILL.md body is {len(body)} lines (> {MAX_BODY_LINES}); "
            "move bulk into reference.md/examples.md/scripts/templates."
        )

    errors.extend(_validate_completion_gate(skill_dir, body))

    # Resolve relative links referenced in SKILL.md.
    for target in LINK_PAT.findall(text):
        target = target.strip()
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        rel = target.split("#", 1)[0]
        if not rel:
            continue
        if not (skill_dir / rel).exists():
            errors.append(f"Broken relative link in SKILL.md: {target!r}.")

    _report(errors, warnings)
    return 1 if errors else 0


def _report(errors, warnings):
    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if not errors:
        print("OK: skill passes structural validation."
              + (f" ({len(warnings)} warning(s))" if warnings else ""))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
