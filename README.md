# AI_agents

This repository contains a sample email-forwarding agent that connects to an inbox using an MCP-style server configuration, filters messages from `example1@test.com`, and forwards matching messages to `sender2@test.com`.

## Included files
- `mail_inbox_forward_agent.py` — Python agent that connects to IMAP, filters sender, forwards matching messages via SMTP.
- `mcp_server_config.json` — sample MCP server configuration for the agent.

## Setup
1. Fill in the real IMAP and SMTP credentials in the environment variables or config.
2. Update `FILTER_SENDER` and `FORWARD_TO` if needed.
3. Run:

```bash
python mail_inbox_forward_agent.py
```

## Environment variables
- `IMAP_HOST`
- `IMAP_PORT` (default: `993`)
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `SMTP_HOST`
- `SMTP_PORT` (default: `587`)
- `FILTER_SENDER` (default: `example1@test.com`)
- `FORWARD_TO` (default: `sender2@test.com`)

This is a starter implementation for an MCP-compatible mail agent and should be adapted to the actual mail provider or server implementation you are using.
