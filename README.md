# AI Project OS

[![PyPI Version](https://img.shields.io/pypi/v/ai-project-os-mcp)](https://pypi.org/project/ai-project-os-mcp/)
[![License](https://img.shields.io/pypi/l/ai-project-os-mcp)](https://pypi.org/project/ai-project-os-mcp/)
[![Python Versions](https://img.shields.io/pypi/pyversions/ai-project-os-mcp)](https://pypi.org/project/ai-project-os-mcp/)

**AI Project Operating System**  
Turn AI coding into real, auditable software engineering.

## What is this?

AI Project OS is an engineering-grade operating system for AI-driven software projects.

It does **not** try to make AI "smarter".  
It makes AI **obedient to real-world engineering rules**.

AI Project OS enforces:
- Clear project stages
- Frozen decisions
- Guarded code generation
- Mandatory audit trails

No freeze, no code.  
No audit, no ship.

## Why AI Project OS?

AI coding fails in real projects because:

- AI skips steps
- AI rewrites architecture
- AI patches instead of redesigning
- Humans cannot tell when AI crossed the line

AI Project OS fixes this by introducing **engineering governance**.

## Core Concepts

### 1. State over Prompt
Project truth lives in `state.json`, not in conversation memory.

### 2. Freeze over Generate
All decisions must be frozen before execution.

### 3. Audit over Output
Code without audit is not considered done.

## The 5S Workflow

| Stage | Meaning | Code Allowed | 
|------|--------|--------------|
| S1 | Scope | ❌ |
| S2 | Spec | ❌ |
| S3 | Structure | ❌ |
| S4 | Schedule | ❌ |
| S5 | Ship | ✅ |

## MCP-Based Governance

AI Project OS is implemented as a **Model Context Protocol (MCP)** server.

This allows:
- Claude
- Cursor
- Trae
- Local agents

To act as **governed engineering executors**, not free-form chatbots.

## S5 Stability Guard (Mandatory)

Every S5 task must include:

- **Context Refresh**
- **Change Fuse**
- **Pseudo-TDD**
- **Audit Record**

No exception.

## Who is this for?

- Non-technical founders
- Product managers using AI coding
- Teams tired of AI-generated mess
- Anyone who wants AI to behave like a real engineer

## Status

**v1.0 — Engineering Governance Stable**

## License

MIT License

## Quick Start

### Installation

```bash
pip install ai-project-os-mcp
```

### Usage

1. **Initialize a new project**:
   ```bash
   ai-project-os init my-project
   cd my-project
   ```

2. **Start with S1 Scope stage**:
   ```bash
   ai-project-os s1
   ```

3. **Follow the 5S workflow**:
   ```bash
   # After completing S1, move to S2
   ai-project-os s2
   
   # Then S3, S4, and finally S5
   ai-project-os s3
   ai-project-os s4
   ai-project-os s5
   ```

4. **Check project status**:
   ```bash
   ai-project-os status
   ```

### For Non-Technical Users

If you don't want to use the command line, check out our [Zero-Code Guide](docs/example-no-code.md) to use AI Project OS with just your AI tool.

## MCP Server Runtime Modes

| Mode | Usage | Security Features |
|------|-------|------------------|
| STDIO | Claude / Cursor / Trae | Lightweight, for development |
| HTTP | Dashboard / Enterprise | Supports authentication, for production |

## Core Principle

> **拒绝违规执行**
> **比勉强完成任务更正确**

AI Project OS believes that refusing to execute violations is more correct than勉强 completing tasks.

## Version Semantics

We follow **Semantic Versioning**:

- **MAJOR (x.0.0)**: Governance model or MCP protocol changes
- **MINOR (1.x.0)**: New governance capabilities, backward compatible
- **PATCH (1.0.x)**: Bug fixes, documentation, or non-behavioral changes

## Release & Rollback Policy

- **Release**: Git tags trigger GitHub Actions for automatic PyPI publishing
- **Rollback**: Never delete published versions, only release fix versions (e.g., v1.0.1)

## Enterprise Edition Roadmap

The following capabilities are reserved for future enterprise editions:

- Multi-project isolation
- Centralized audit logging
- Private MCP Registry
- SSO / RBAC support

## Philosophy

> AI should not be creative about structure.  
> AI should be creative only within frozen boundaries.
