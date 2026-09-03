# Skill Authoring Reference

Full rules behind the [SKILL.md](SKILL.md) workflow. A `SKILL.md` should be a small, reusable task
playbook for an agent: repeatable workflows that benefit from richer instructions, references, or
scripts without bloating always-on context. `AGENTS.md` is for durable project guidance that applies
before work starts.

## What goes where

- `AGENTS.md` lives at repo level and contains repo-wide defaults, conventions, and guardrails.
- Each skill lives in its own directory.
- `SKILL.md` is the entry point for that skill.
- `scripts/` contains deterministic helpers used by that skill.
- `reference.md`, `examples.md`, and `templates/` contain supporting material for that skill.

## 8 core rules

### 1. One skill, one job

Keep each skill narrowly scoped. Start from a few concrete use cases, define clear inputs and
outputs, and only add scripts/assets when they improve reliability.

Good: `debugging-flaky-pytest`, `generating-release-notes-from-prs`
Bad: `testing helper`, `backend workflow`

If the name sounds vague, the scope is probably too broad.

### 2. The description is the router

The description is the most important line in the skill and is critical for skill selection. It
should say:

- what the skill does
- when to use it
- enough trigger wording that the agent can pick it reliably

Bad:

```md
description: Generate release notes
```

Better:

```yaml
description: >-
  Generate a markdown changelog from merged PRs since the last tag, grouped by
  conventional-commit type. Use when asked for release notes, a changelog, or "what changed since X".
```

For simple skills the description is enough. Only add separate "use this skill when" /
"do not use this skill when" sections when the boundary is easy to get wrong.

### 3. Keep `SKILL.md` small

Keep the main `SKILL.md` body under 500 lines and move bulk into separate files using progressive
disclosure:

- `reference.md`
- `examples.md`
- `templates/`
- `scripts/`

A good `SKILL.md` is usually a dispatcher plus workflow.

### 4. Write procedures, not essays

Use explicit workflows and feedback loops. A skill should mostly say:

- inspect these files
- run this command
- if this case happens, follow this branch
- validate
- fix and rerun if needed

Prefer explicit steps over explanation.

### 5. Script deterministic work

Utility scripts are more reliable than regenerated code, save tokens, and improve consistency. Use
scripts for things the model should not keep reinventing:

- parsing logs
- extracting structured fields
- normalizing data
- generating reports
- validating output
- running fixed command sequences
- if applicable, summarizing file changes / additions

Keep scripts runnable outside any specific agent runtime.

### 6. Make scripts tiny CLIs

Design skill scripts like small command-line tools with clear documentation and explicit error
handling. A helper script should usually document just:

- purpose
- usage
- exit behavior
- requirements (e.g. access tokens, libraries)

Example:

```py
#!/usr/bin/env python3
"""
Purpose: Extract failing tests from CI logs.

Usage:
    python3 scripts/extract_failures.py <log_dir>
"""
```

If the script writes a file, note the output path too.

### 7. Include execution-time validation

Every nontrivial skill should include an explicit validation step that runs while the skill is being
executed: validate immediately, inspect the error, fix, rerun, and only proceed once validation
passes. Cap reruns (e.g. 2-3 times) to prevent thrashing.

Include:

- a concrete validator, test, or linter command
- a fix-and-rerun loop
- clear stop conditions for when the agent should report instead of thrashing

Default loop:

1. do the work
2. run validator/test/linter
3. inspect failure
4. repair
5. rerun

Example validators:

- `pytest tests/integration/test_auth.py -q`
- `go test ./cmd/foo/...`
- `python scripts/validate_manifest.py out/manifest.json`

Treat this as part of the skill's runtime workflow.

### 8. Evaluate the skill with test prompts

Separately from runtime validation, each skill should have a small set of author-side evaluation
prompts to check whether the agent triggers the skill when it should, and avoids triggering it when
it should not. Measure trigger behavior, process-following, style, and efficiency.

Keep 2-4 prompts:

- one clear positive trigger
- one near-miss / out-of-scope case
- optionally one edge case

Put prompts in a separate file, e.g. `examples.md`. See [examples.md](examples.md).

## Supporting files

Supporting files can be longer than `SKILL.md`, but they should be skimmable:

- use headings
- use stable anchors
- keep links shallow
- avoid deep chains of references

## Optional sections

Only add these to a `SKILL.md` when needed:

- `Inputs`
- `Outputs`
- `Stop and report if`
- `Use this skill when`
- `Do not use this skill when`

## Short checklist

Before merging a skill:

- Is the scope narrow?
- Is the description specific and triggerable?
- Is the workflow executable?
- Is validation explicit?
- Did bulky detail move out of `SKILL.md`?
- Should any step be a script instead?
- Are there 2-4 evaluation prompts for routing and behavior?

## Source basis

- Anthropic, **Agent Skills overview** — skills as modular capabilities with metadata,
  instructions, and optional resources loaded progressively.
- Anthropic, **Skill authoring best practices** — descriptions, compact `SKILL.md`, progressive
  disclosure, workflows, validation loops, scripts, and testing.
- OpenAI, **Codex best practices** — one skill, one job; clear inputs/outputs; description should
  say what the skill does and when to use it.
- OpenAI, **AGENTS.md guide** — `AGENTS.md` as layered project guidance.
- OpenAI, **Testing Agent Skills Systematically with Evals** — test trigger behavior, process,
  style, and efficiency.
