#!/usr/bin/env python3
"""Focused CLI tests for validate_skill.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

VALIDATOR = Path(__file__).parents[1] / "scripts" / "validate_skill.py"

VALID_BODY = """# Sample skill

## Workflow

1. Perform the requested work.
2. Validate it: `python3 -m unittest`
3. If validation fails, fix the issue and rerun the command.
4. Stop after 3 attempts and report the remaining failure.
"""

VALID_EXAMPLES = """# Examples

Example test prompts:

Positive:
- "Run the sample task."

Near-miss / should not trigger:
- "Explain the sample task."

Edge case:
- "Run the sample task with empty input."
"""


class ValidateSkillTests(unittest.TestCase):
    def run_validator(
        self,
        body=VALID_BODY,
        examples=VALID_EXAMPLES,
        frontmatter=None,
    ):
        if frontmatter is None:
            frontmatter = (
                "name: sample-skill\n"
                "description: Perform a focused sample task. Use when asked to test "
                "skill validation behavior."
            )

        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "sample-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\n" + frontmatter.rstrip() + "\n---\n\n" + body,
                encoding="utf-8",
            )
            if examples is not None:
                (skill_dir / "examples.md").write_text(examples, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(skill_dir)],
                check=False,
                capture_output=True,
                text=True,
            )

    def test_compliant_skill_passes(self):
        result = self.run_validator()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("OK: skill passes structural validation.", result.stdout)

    def test_folded_yaml_description_passes(self):
        frontmatter = """name: sample-skill
description: >-
  Perform a focused sample task with correctly parsed YAML metadata.
  Use when asked to test skill validation behavior.
"""
        result = self.run_validator(frontmatter=frontmatter)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_malformed_yaml_fails_without_traceback(self):
        frontmatter = """name: sample-skill
description: Perform a focused sample task. Use when asked to test validation.
broken: [one, two
"""
        result = self.run_validator(frontmatter=frontmatter)

        self.assertEqual(1, result.returncode)
        self.assertIn("invalid YAML frontmatter", result.stdout)
        self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_frontmatter_fields_must_be_strings(self):
        frontmatter = """name:
  - sample-skill
description:
  - Perform a focused sample task.
  - Use when asked to test validation.
"""
        result = self.run_validator(frontmatter=frontmatter)

        self.assertEqual(1, result.returncode)
        self.assertIn("`name` must be a non-empty string", result.stdout)
        self.assertIn("`description` must be a non-empty string", result.stdout)

    def test_workflow_section_is_required(self):
        result = self.run_validator(body=VALID_BODY.replace("## Workflow", "## Steps"))

        self.assertEqual(1, result.returncode)
        self.assertIn("missing a `Workflow` section", result.stdout)

    def test_unresolved_template_placeholder_fails(self):
        result = self.run_validator(body=VALID_BODY + "\n- `<command or script>`\n")

        self.assertEqual(1, result.returncode)
        self.assertIn("unresolved template placeholder", result.stdout)

    def test_validation_command_and_bounded_repair_loop_are_required(self):
        body = """# Sample skill

## Workflow

1. Perform the requested work.
2. Return the result.
"""
        result = self.run_validator(body=body)

        self.assertEqual(1, result.returncode)
        self.assertIn("missing a concrete validator/test/linter command", result.stdout)
        self.assertIn("missing an explicit fix-and-rerun loop", result.stdout)
        self.assertIn("missing a 2-3 attempt/rerun limit", result.stdout)

    def test_examples_file_is_required(self):
        result = self.run_validator(examples=None)

        self.assertEqual(1, result.returncode)
        self.assertIn("Missing examples.md with 2-4 eval prompts", result.stdout)

    def test_eval_prompt_count_and_categories_are_checked(self):
        examples = """# Examples

## Eval prompts

Positive:
- "Prompt one."
- "Prompt two."
- "Prompt three."
- "Prompt four."
- "Prompt five."
"""
        result = self.run_validator(examples=examples)

        self.assertEqual(1, result.returncode)
        self.assertIn("contains 5 prompt(s); expected 2-4", result.stdout)
        self.assertIn("missing a near-miss/out-of-scope case", result.stdout)


if __name__ == "__main__":
    unittest.main()
