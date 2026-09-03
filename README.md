# openstack-agentic-skills

A collection of GitHub Copilot agent skills for OpenStack / Sunbeam development workflows.

## Skills

| Skill | Description |
|---|---|
| [cinder-spec-generator](cinder-spec-generator/SKILL.md) | Extracts oslo.config options from Cinder volume driver source and generates driver-spec YAML files for sunbeam-cinder-factory |
| [diagnose-sunbeam](diagnose-sunbeam/SKILL.md) | Diagnoses failed Sunbeam CI runs by analyzing sosreport tarballs, juju status files, and sunbeam CLI logs for multi-node OpenStack deployment failures on Canonical K8s |
| [lxd](lxd/SKILL.md) | Workflows for LXD containers and VMs: launching Ubuntu instances, mounting host directories and storage volumes, defining reusable profiles and networks, and avoiding common automation hangs |
| [plot-fio-results](plot-fio-results/README.md) | Generates a 4-panel matplotlib chart (throughput, IOPS, latency, scaling efficiency) from rally-ci-churn fio benchmark result files |
| [reviewskill](reviewskill/SKILL.md) | Prepare and perform deterministic all-rubric code reviews for working-tree changes, branch/range diffs, GitHub pull requests, or complete repositories |
| [sunbeam-networking](sunbeam-networking/SKILL.md) | Lab networking knowledge for Sunbeam/OpenStack: NICs, bonds, fabrics, VLANs, MAAS interface configuration, Juju space mapping, and onboarding guidance |

## OpenCode Install

### Quick

The fastest way is to tell OpenCode:

```
Clone https://github.com/canonical/openstack-agentic-skills to ~/.config/opencode/openstack-agentic-skills, then create directory ~/.config/opencode/plugins, then symlink ~/.config/opencode/openstack-agentic-skills to ~/.config/opencode/skills/openstack-agentic-skills, then restart opencode.
```

### Manual

1. Create directories

```
mkdir -p ~/.config/opencode
mkdir -p ~/.config/opencode/skills
```

2. Clone openstack-agentic-skills

``` sh
cd ~/.config/opencode
git clone https://github.com/canonical/openstack-agentic-skills
```

3. Create skills symlink

```
ln -s ~/.config/opencode/openstack-agentic-skills ~/.config/opencode/skills/openstack-agentic-skills
```

4. Restart OpenCode

5. Verify installation running `opencode` and executing the command `/skills`.

---

## Guidelines

When adding or editing a skill, follow the conventions in [Skill Authoring Guide](docs/skill-writing-guidelines.md): narrow scope, a trigger-friendly description, a compact `SKILL.md`, explicit workflows, deterministic scripts, runtime validation, and a small set of evaluation prompts.

---

## cinder-spec-generator

### Configuration

1. **Copy the skill into your project's agent skills directory:**

   ```bash
   cp -r cinder-spec-generator /path/to/your/project/.agents/skills/
   ```

2. **Register the skill** by referencing it in your VS Code Copilot configuration (`.github/copilot-instructions.md` or workspace `.vscode/settings.json`), or place the skill directory under `.agents/skills/` in the target repository so Copilot picks it up automatically.

3. **Install the Python dependency:**

   ```bash
   pip install pyyaml
   ```

4. **Ensure a Cinder source tree is accessible** (default expected location: `../cinder` relative to your working repo).

### Usage

Invoke the skill via Copilot chat by describing what you want, e.g.:

> *"Generate a driver spec for the Pure Storage Cinder driver"*

See [cinder-spec-generator/SKILL.md](cinder-spec-generator/SKILL.md) for the full workflow, all options, and reference material.

---

## lxd

Symlink the skill into your agent skills directory:

```bash
mkdir -p /path/to/your/project/.agents/skills
ln -s /path/to/openstack-agentic-skills/lxd /path/to/your/project/.agents/skills/lxd
```

Ensure LXD is available and the current user can run `lxc`:

```bash
lxc info
lxc image info ubuntu:26.04
```

The skill covers LXD container and VM launch patterns, readiness checks, host mounts, VM storage volumes, reusable profiles, managed bridge networks, and automation hang troubleshooting.

Validate from the `lxd` skill directory:

```bash
./tests/smoke.sh
```

See [lxd/SKILL.md](lxd/SKILL.md) for details.

---

## Contributing

Contributions are welcome — feel free to open a pull request with new skills or improvements to existing ones.
