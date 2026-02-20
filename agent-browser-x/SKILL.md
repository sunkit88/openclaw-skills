---
name: agent-browser-x
description: Open and interact with X.com (Twitter) using agent-browser with AWS Bedrock AgentCore Browser and profile persistence. Use this skill when the user asks to browse X, check tweets, or interact with X.com.
---

# Agent-Browser X Skill

This skill uses `agent-browser` with AWS Bedrock AgentCore Browser to open X.com in a persistent, authenticated browser session.

## Prerequisites

- `agent-browser` installed globally (PR #397 with AgentCore support)
- AWS credentials configured (`~/.aws/credentials`)
- IAM user with `bedrock-agentcore:*` permissions
- Browser profile created in AWS Console with saved X.com login cookies

## Environment Variables

```bash
export AGENTCORE_REGION=eu-west-2
export AGENTCORE_PROFILE_ID="x_profile_zsj0u-LAFp3Bq7dv"
```

## Usage

### 1. Open X.com (authenticated)

```bash
pkill -f agent-browser 2>/dev/null; sleep 1
export AGENTCORE_REGION=eu-west-2
export AGENTCORE_PROFILE_ID="x_profile_zsj0u-LAFp3Bq7dv"
agent-browser -p agentcore open https://x.com/home --timeout 30000 2>&1
```

> Note: `page.goto: Timeout` is common for X.com. Use `agent-browser snapshot` to check if page loaded.

### 2. Interact with the page

```bash
agent-browser snapshot                    # Check page content
agent-browser eval "document.title"       # Evaluate JavaScript
agent-browser click --ref e9              # Click elements (use ref from snapshot)
agent-browser type --ref e5 "search term" # Type text
```

### 3. Navigate to specific pages

```bash
agent-browser open https://x.com/home --timeout 30000 2>&1           # Home
agent-browser open https://x.com/explore --timeout 30000 2>&1        # Explore
agent-browser open https://x.com/notifications --timeout 30000 2>&1  # Notifications
agent-browser open https://x.com/<username> --timeout 30000 2>&1     # User profile
```

### 4. Close browser session

```bash
agent-browser close
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Could not load credentials` | Kill stale daemon: `pkill -f agent-browser` then retry |
| `page.goto: Timeout` | Normal for X.com. Run `agent-browser snapshot` to check |
| Login page shown | Profile cookies expired. Re-login via Live View and re-save profile |
| `Browser profile not found` | Profile must be created in AWS Console first |

## Re-saving Profile (when cookies expire)

1. Open session with profile (use commands above)
2. Login in AWS Console Live View
3. Get session ID:
   ```bash
   aws bedrock-agentcore list-browser-sessions \
     --browser-identifier aws.browser.v1 \
     --region eu-west-2 --no-cli-pager --output json 2>&1 \
     | grep -E "sessionId|status"
   ```
4. Save profile:
   ```bash
   aws bedrock-agentcore save-browser-session-profile \
     --profile-identifier "x_profile_zsj0u-LAFp3Bq7dv" \
     --browser-identifier aws.browser.v1 \
     --session-id <SESSION_ID> \
     --region eu-west-2 --no-cli-pager
   ```
