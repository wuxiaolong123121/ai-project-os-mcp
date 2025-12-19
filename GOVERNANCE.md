# AI Project OS Governance

## Purpose

AI Project OS exists to define **engineering boundaries** for AI-driven software development.

This project prioritizes:
- Determinism over creativity
- Governance over convenience
- Auditability over speed

## Decision Authority

- Humans own decisions
- AI executes frozen instructions
- No AI may override frozen stages

## Contribution Rules

Contributions must:
- Respect the 5S workflow
- Not weaken guard mechanisms
- Not allow silent architecture changes
- Preserve audit requirements

PRs that reduce enforcement strength will be rejected.

## Design Principles (Non-Negotiable)

1. No code generation before S5
2. No architecture modification without S3 refreeze
3. No S5 work without audit
4. No hidden state or implicit behavior

## Rejected Ideas

The following will not be accepted:
- "Let AI decide dynamically"
- "Relax rules for speed"
- "Auto-fix architecture silently"
- "Optional audit"

## Maintainer Authority

Maintainers reserve final decision authority on:
- Protocol changes
- Rule enforcement
- MCP compatibility

This project is governance-first by design.
