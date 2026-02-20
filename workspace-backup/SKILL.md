---
name: workspace-backup
description: Backup OpenClaw workspace-* folders to GitHub repo sunkit88/openclaw_workspaces. Use this skill when the user asks to backup workspaces, sync workspace changes, or push workspace updates to GitHub.
---

# Workspace Backup Skill

Backs up all `~/.openclaw/workspace-*` folders to the private GitHub repo `sunkit88/openclaw_workspaces`.

## Prerequisites

- Git configured with SSH key for GitHub (`~/.ssh/id_ed25519`)
- GitHub repo: `git@github.com:sunkit88/openclaw_workspaces.git` (private)

## Usage

### Full Backup (overwrite)

```bash
cd /tmp && rm -rf openclaw_workspaces
git clone git@github.com:sunkit88/openclaw_workspaces.git
cd openclaw_workspaces

# Remove old workspace copies
rm -rf workspace-*

# Copy fresh workspaces
cp -r ~/.openclaw/workspace-* .

# Remove nested .git dirs
find . -mindepth 2 -name ".git" -type d -exec rm -rf {} + 2>/dev/null

# Commit and push
git add -A
git commit -m "Workspace backup $(date +%Y-%m-%d_%H%M)"
git push origin main
```

### Quick Sync (incremental)

```bash
cd /tmp/openclaw_workspaces 2>/dev/null || (cd /tmp && git clone git@github.com:sunkit88/openclaw_workspaces.git && cd openclaw_workspaces)

# Sync workspaces
rsync -av --delete --exclude='.git' ~/.openclaw/workspace-*/ ./ 2>/dev/null || {
  rm -rf workspace-*
  cp -r ~/.openclaw/workspace-* .
  find . -mindepth 2 -name ".git" -type d -exec rm -rf {} + 2>/dev/null
}

git add -A
git diff --cached --quiet || git commit -m "Workspace sync $(date +%Y-%m-%d_%H%M)" && git push origin main
```

## Workspaces Included

| Workspace | Description |
|-----------|-------------|
| workspace-FlatWhite | FlatWhite agent workspace |
| workspace-Latte | Latte agent workspace |
| workspace-Mocha | Mocha agent workspace (main) |

## Notes

- Repo is **private** — only `sunkit88` can access
- Nested `.git` directories are stripped before commit
- Each workspace contains: IDENTITY.md, SOUL.md, AGENTS.md, TOOLS.md, USER.md, HEARTBEAT.md, memory/
