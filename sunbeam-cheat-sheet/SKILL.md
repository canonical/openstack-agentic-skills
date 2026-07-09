---
name: sunbeam-cheat-sheet
description: "Developer notepad of known Sunbeam / Canonical OpenStack (snap-openstack) problems, errors, and their proven workarounds. Use when: a Sunbeam or snap-openstack deployment fails; hitting a known error message during 'sunbeam cluster bootstrap/deploy', K8S/Terraform/Juju/charm steps, MAAS mode, Cilium/MetalLB/CNI issues, or any OpenStack service failure; a developer asks 'has this bug happened before?', 'what's the workaround for X?', 'how did we fix Y?'. Also use to RECORD a new problem+workaround so other developers can find it later instead of asking around."
argument-hint: "an error message / symptom to look up, OR 'add' + the problem and its workaround to record a new entry"
---

# Sunbeam Cheat Sheet

A shared, growing knowledge base of real Sunbeam / Canonical OpenStack problems and
their verified workarounds. It is a **developer notepad**: developers keep adding
entries so others can look up a fix instead of asking around.

## Execution policy (MANDATORY)

**NEVER run any command yourself.** Only the developer runs commands.

- Always present a workaround **as commands / manifest snippets for the developer
  to run**, inside code blocks. Do not execute them via any terminal/run tool.
- This applies to everything: `juju`, `sunbeam`, `kubectl`, `maas`, `terraform`,
  diagnostics, "just checking" reads — all of it. Provide the command; the
  developer decides whether to run it.
- If you need output to continue, ask the developer to run the command and paste
  the result back. Do not run it for them.

## When to use

- **Look up a fix:** a deployment failed with some error/symptom → search the
  cheat sheet for a matching known issue and return the documented workaround.
- **Record a new fix:** a developer hit a new problem and found a workaround →
  add a new entry so it is searchable next time.

## How to look up a workaround

1. Read [references/entries.md](./references/entries.md) — the full list of known issues.
2. Match the user's error message / symptom to an entry (search by the key error
   string, the failing step, or the component: Cilium, MetalLB, Juju, MAAS, Terraform, etc.).
3. Return the **Workaround** as copy-paste commands / manifest for the developer to
   run (never run it yourself — see Execution policy), and note the **Root cause**.
4. If nothing matches, say so clearly — do not invent a fix. Offer to record it once solved.

## How to add a new entry

When the user says "add", "record this", "save this workaround", or describes a
solved problem, append a new entry to [references/entries.md](./references/entries.md)
using the template at the top of that file. Fill in every field:

- **Title** — short, searchable summary of the symptom
- **Component / Step** — e.g. `k8s / Terraform apply`, `MAAS mode`, `Juju`
- **Symptom** — the exact error message(s) and observable behavior (copy verbatim)
- **Root cause** — why it happens
- **Workaround** — the exact commands / manifest snippet that fixes it
- **Notes** — gotchas, links, bug references, date, who confirmed it

Keep entries concise and paste **exact** error strings and commands so future
searches match. Prefer declarative fixes (manifest) over live `juju config` where both exist.

## Growth rule

Keep this `SKILL.md` small. All actual knowledge lives in `references/entries.md`.
When that file grows large (many categories), split it by component into separate
files under `references/` (e.g. `references/k8s.md`, `references/maas.md`,
`references/juju.md`) and link them from here.

## References

- [references/entries.md](./references/entries.md) — the searchable list of known issues + workarounds.
