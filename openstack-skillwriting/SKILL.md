---
name: openstack-skillwriting
description: Author, review, and validate agent SKILL.md files that follow the Skill Authoring Guide (focused scope, triggerable description, compact main file, progressive disclosure, explicit workflow, deterministic scripts, runtime validation, and eval prompts). Use when asked to write a new skill, create a SKILL.md, improve or refactor an existing skill, or check whether a skill follows best practices.
---

# Skill Writing

Turns a task idea into a well-formed agent skill: a compact `SKILL.md` dispatcher plus optional
reference, examples, scripts, and templates. Resolve all relative paths below against this skill
directory.

Requirements: `python3` and PyYAML for the validator. Install it with
`python3 -m pip install PyYAML`.

## Workflow

1. **Scope the skill (one skill, one job).**
   - Get the single repeatable task it automates and 1-3 concrete use cases.
   - Pick a specific, verb-based directory name (e.g. `generating-release-notes-from-prs`),
     not a vague one (`backend workflow`). If the name sounds vague, the scope is too broad.
   - See rule 1 in [reference.md](reference.md#1-one-skill-one-job).

2. **Write the description first — it is the router.**
   - State *what it does* and *when to use it*, with trigger wording an agent can match.
   - Add explicit "use when" / "do not use when" lines only if the boundary is easy to miss.
   - See rule 2 in [reference.md](reference.md#2-the-description-is-the-router).

3. **Draft a compact `SKILL.md` from the template.**
   - Copy [templates/SKILL.md.template](templates/SKILL.md.template).
   - Keep the body under 500 lines; write numbered procedures, not essays.
   - Move bulk into `reference.md`, `examples.md`, `templates/`, `scripts/`
     (progressive disclosure). See rules 3-4 in [reference.md](reference.md#3-keep-skillmd-small).

4. **Move deterministic work into tiny CLI scripts.**
   - Anything the model should not reinvent (parsing, extracting, normalizing, reporting,
     validating, fixed command sequences) belongs in `scripts/`.
   - Each script documents purpose, usage, exit behavior, requirements, and output path.
   - See rules 5-6 in [reference.md](reference.md#5-script-deterministic-work).

5. **Add an execution-time validation loop to the skill you are writing.**
   - Include a concrete validator/test/linter command plus a fix-and-rerun loop, capped at
     2-3 reruns before reporting instead of thrashing.
   - See rule 7 in [reference.md](reference.md#7-include-execution-time-validation).

6. **Add 2-4 author-side eval prompts.**
   - One clear positive trigger, one near-miss/out-of-scope, optionally one edge case.
   - Put them in `examples.md`. See rule 8 in [reference.md](reference.md#8-evaluate-the-skill-with-test-prompts)
     and the sample set in [examples.md](examples.md).

7. **Validate the skill structure.**
   - Run: `python3 scripts/validate_skill.py <path/to/skill-dir>`
   - If it fails, inspect the reported issues, fix the skill, and rerun.
   - Stop after 3 rerun attempts and report remaining issues instead of thrashing.

8. **Run the final checklist** in [reference.md](reference.md#short-checklist) before declaring done.

## Supporting files

- [reference.md](reference.md) — the 8 core rules in full, supporting-file guidance, checklist, and source basis
- [examples.md](examples.md) — eval prompts for this skill and a sample eval set for a generated skill
- `templates/SKILL.md.template` — minimal `SKILL.md` skeleton to copy
- `scripts/validate_skill.py` — deterministic structural validator for a skill directory
- `requirements.txt` — validator dependency
