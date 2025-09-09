# Security Mediator for Jarvis

## Overview
The Security Mediator is a critical component of Jarvis that enforces security policies and requires user confirmation for high-risk actions. It acts as an active security layer that decouples the agent's reasoning from execution, ensuring safe operation.

## Architecture
- **SecurityMediator Class**: Intercepts all agent tool calls before execution.
- **Policy Enforcement**: Checks each tool call against configurable policies.
- **Confirmation Prompts**: Uses TTS to request verbal confirmation for high-risk actions, verified via speaker authentication.

## Policies
The mediator enforces the following policies:

### NEVER_DELETE_WITHOUT_CONFIRMATION
- **Type**: Boolean
- **Default**: True
- **Description**: Requires confirmation for any delete operations.

### BLACKLIST_PATHS
- **Type**: List of strings
- **Default**: ['/system', '/root', 'C:/Windows', 'C:/Program Files']
- **Description**: Blocks access to specified paths. Any tool call with a 'path' parameter starting with a blacklisted path is rejected.

### HIGH_RISK_ACTIONS
- **Type**: List of strings
- **Default**: ['delete', 'remove', 'uninstall', 'format']
- **Description**: Actions containing these keywords require verbal confirmation.

## Usage
The SecurityMediator is automatically integrated into the agent loop. All tool calls are routed through the mediator:

```python
from security_mediator import security_mediator

# Tool calls are automatically secured
result = security_mediator.execute_tool(tool_function, tool_name, *args, **kwargs)
```

## Confirmation Process
For high-risk actions:
1. TTS announces the action and requests confirmation.
2. Records user's response.
3. Verifies speaker using voiceprint.
4. Transcribes response using Whisper.
5. Accepts 'yes' or 'confirm' as approval.

## Integration
- Tools are wrapped with `SecureTool` class in `agent.py`.
- All LangChain tool executions pass through the mediator.
- No changes required to existing tool implementations.

## Testing
Run tests with:
```bash
cd src
python -m unittest test_security_mediator.py
```

Tests cover:
- Policy violations
- Confirmation prompts
- Tool execution with/without confirmation
- Speaker verification mocks

## Security Considerations
- Voiceprint must be enrolled before using confirmation features.
- Blacklisted paths prevent access to critical system areas.
- All high-risk actions require explicit user approval.
- Failed confirmations result in action rejection.

## Future Enhancements
- Configurable policies via external file.
- Additional authentication methods.
- Audit logging of security events.
- Integration with external security systems.