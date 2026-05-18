from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_AGENT_FIELDS = {"name", "description", "developer_instructions"}
REQUIRED_SKILL_FIELDS = {"name", "description"}


def parse_skill_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter")

    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("unterminated frontmatter")

    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def main() -> int:
    errors: list[str] = []

    config_path = ROOT / ".codex" / "config.toml"
    if not config_path.exists():
        errors.append("missing .codex/config.toml")
    else:
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
        agents = config.get("agents", {})
        if agents.get("max_threads") != 6:
            errors.append(".codex/config.toml agents.max_threads must be 6")
        if agents.get("max_depth") != 1:
            errors.append(".codex/config.toml agents.max_depth must be 1")

    agent_dir = ROOT / ".codex" / "agents"
    agent_files = sorted(agent_dir.glob("*.toml"))
    if not agent_files:
        errors.append("no custom agents found in .codex/agents")

    for path in agent_files:
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"{path.relative_to(ROOT)} invalid TOML: {exc}")
            continue

        missing = REQUIRED_AGENT_FIELDS - data.keys()
        if missing:
            errors.append(f"{path.relative_to(ROOT)} missing fields: {sorted(missing)}")
        if data.get("name") != path.stem:
            errors.append(f"{path.relative_to(ROOT)} name must match file stem")

    skills_dir = ROOT / ".agents" / "skills"
    skill_files = sorted(skills_dir.glob("*/SKILL.md"))
    if not skill_files:
        errors.append("no repo skills found in .agents/skills")

    for path in skill_files:
        try:
            fields = parse_skill_frontmatter(path)
        except ValueError as exc:
            errors.append(f"{path.relative_to(ROOT)} {exc}")
            continue

        missing = REQUIRED_SKILL_FIELDS - fields.keys()
        if missing:
            errors.append(f"{path.relative_to(ROOT)} missing frontmatter: {sorted(missing)}")
        if fields.get("name") != path.parent.name:
            errors.append(f"{path.relative_to(ROOT)} name must match skill directory")

    if errors:
        print("Codex team config check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Codex team config OK: "
        f"{len(agent_files)} agents, {len(skill_files)} skills, config verified."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
