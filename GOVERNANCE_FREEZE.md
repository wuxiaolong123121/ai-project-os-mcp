# AI Project OS v2.5 - Governance Kernel Freeze Rules

## 1. Core Modules That MUST NOT Be Modified

The following core modules constitute the "Spec Frozen" governance kernel and MUST NOT be modified without a major version bump:

### 1.1 Governance Engine and Core Engines
- `ai_project_os_mcp/core/governance_engine.py`
- `ai_project_os_mcp/core/state_manager.py`
- `ai_project_os_mcp/core/event_store.py`
- `ai_project_os_mcp/core/policy_engine.py`
- `ai_project_os_mcp/core/trigger_engine.py`
- `ai_project_os_mcp/core/score_engine.py`
- `ai_project_os_mcp/core/violation.py`

### 1.2 Core Models and Events
- `ai_project_os_mcp/core/events.py`
- `ai_project_os_mcp/core/decision_models.py`
- `ai_project_os_mcp/core/human_sovereignty_models.py`
- `ai_project_os_mcp/core/governance_proof_models.py`
- `ai_project_os_mcp/core/governance_attestation.py`

### 1.3 Core Invariants
- `docs/GOVERNANCE_INVARIANTS.md`
- `SECURITY_BOUNDARIES.md`

## 2. Changes That Require Major Version Bump

The following changes require a new major version (v3.0+) and must not be made to v2.5:

### 2.1 Governance Semantics Changes
- Modifying the Single Gate principle
- Changing freeze irreversibility rules
- Altering audit append-only behavior
- Modifying event closure requirements
- Changing violation enforcement mechanics
- Altering state integrity rules

### 2.2 Core Architecture Changes
- Adding new core engines that bypass GovernanceEngine
- Changing event processing flow
- Modifying the state update mechanism
- Adding new governance invariants

### 2.3 Behavior Changes
- Changing how violations are detected
- Modifying policy evaluation order
- Altering score calculation logic
- Changing how freeze/unfreeze works

## 3. Changes That Are Allowed

The following changes are allowed without a major version bump:

### 3.1 Bug Fixes
- Fixing security vulnerabilities
- Fixing logical errors in existing functionality
- Fixing performance issues
- Fixing documentation errors

### 3.2 Non-Core Changes
- Adding new features outside the governance kernel
- Adding new tools or utilities
- Improving test coverage
- Updating dependencies

### 3.3 Documentation Changes
- Improving existing documentation
- Adding examples or tutorials
- Updating README.md
- Adding new non-core documentation

## 4. Behaviors That Break Governance Adjudicability

The following behaviors are strictly prohibited as they break governance adjudicability:

### 4.1 Bypassing GovernanceEngine
- Directly modifying state
- Creating events without going through GovernanceEngine
- Accessing core engines directly

### 4.2 Modifying Audit Records
- Deleting or modifying existing audit records
- Modifying event history
- Modifying violation records

### 4.3 Breaking State Integrity
- Directly modifying state.json
- Creating inconsistent state
- Modifying overlay_states directly

### 4.4 Violating Freeze Irreversibility
- Implementing automatic unfreeze mechanisms
- Allowing unfreeze without proper authorization
- Breaking freeze state within the same stage

## 5. Governance Kernel Extension Points

The following are approved extension points for building on top of the governance kernel:

### 5.1 Adding New Policy Actions
- Extending `_ActionType` enum
- Adding new policy conditions
- Adding new action handlers

### 5.2 Adding New Event Types
- Extending `_EventType` enum
- Adding new event handlers

### 5.3 Adding New Violation Types
- Extending `_ViolationLevel` enum
- Adding new violation detection rules

### 5.4 Adding New Score Components
- Adding new score calculation logic
- Adding new score components

## 6. Version Bump Rules

### 6.1 Major Version (x.0.0)
- Changes to governance semantics
- Changes to core architecture
- Breaking changes to API

### 6.2 Minor Version (1.x.0)
- New features that don't change governance semantics
- New extension points
- Non-breaking API changes

### 6.3 Patch Version (1.0.x)
- Bug fixes
- Documentation updates
- Performance improvements
- Dependency updates

## 7. Release Process for Governance Kernel

Any changes to the governance kernel must follow this process:

1. Create a formal proposal describing the change
2. Review by the governance working group
3. Public announcement
4. Version bump according to the rules above
5. Updated documentation
6. Comprehensive testing of governance invariants

## 8. Consequences of Breaking Freeze Rules

Breaking the freeze rules will:
- Invalid the governance kernel's Spec Frozen status
- Break the trust of users who rely on the governance invariants
- Require a complete re-validation of the governance system
- Potentially invalidate existing audit records

## 9. Governance Kernel Authority

This document constitutes the formal freeze rules for the AI Project OS v2.5 governance kernel. These rules are binding and must be followed by all contributors.

The governance kernel is designed to be a "reference implementation" of AI governance that can be trusted, audited, and adjudicated. Breaking these rules undermines this trust.