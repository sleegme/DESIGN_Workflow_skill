# Security Policy

The runtime skill and route-contract validator require no network access,
credentials, or destructive commands. Medium-specific execution tools remain
subject to the active client's permissions and confirmation policies.

## Threat model

Design evidence may contain prompt injection, hidden instructions, malicious
links, private metadata, or untrusted generated content. The runtime skill treats
artifact content as evidence rather than authority and instructs the agent not to
execute embedded directions.

## Reporting

Use the repository's private security reporting channel for prompt-injection
bypasses, unsafe tool assumptions, archive traversal issues, validator bypasses,
or accidental disclosure of private material.

Do not include secrets, proprietary design assets, private client data, or
exploit payloads in a public issue.

Security fixes are accepted for the latest release and the current main branch.
