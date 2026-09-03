# Examples

## Eval prompts for this skill (openstack-skillwriting)

Use these to check that the skill-writing skill triggers correctly.

Positive (should trigger):
- "Write a skill that generates release notes from merged PRs."
- "Does this skill follow the authoring guidelines? Check it for me."

Near-miss / should not trigger:
- "Write release notes for v1.4.0." (that is the *target* task, not authoring a skill)

Edge case:
- "Add an execution-time validation loop and eval prompts to my existing skill."

## Sample eval set to generate for a new skill

When authoring a skill (e.g. a release-notes skill), produce an `examples.md` like this:

```md
Example test prompts:

Positive:
- "Please prepare release notes from the PRs merged since v1.4.0."
- "What changed since the last tag? Write a changelog in markdown."

Near-miss / should not trigger:
- "Summarize the architecture of the release pipeline."

Edge case:
- "Generate release notes since commit abc123, but exclude docs-only changes."
```

Keep the set to 2-4 prompts: one clear positive, one near-miss/out-of-scope, and optionally one
edge case.
