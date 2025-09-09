import os
from typing import Any, Dict, List, Callable
from voice import speak, verify_speaker, record_command_audio, transcribe_audio

class SecurityMediator:
    def __init__(self, policies: Dict[str, Any] = None):
        self.policies = policies or self.default_policies()

    def default_policies(self) -> Dict[str, Any]:
        return {
            'NEVER_DELETE_WITHOUT_CONFIRMATION': True,
            'BLACKLIST_PATHS': ['/system', '/root', 'C:/Windows', 'C:/Program Files'],
            'HIGH_RISK_ACTIONS': ['delete', 'remove', 'uninstall', 'format']
        }

    def check_policy(self, tool_name: str, tool_input: Dict[str, Any]) -> bool:
        """Check if the tool call violates any policies. Return True if allowed, False if blocked."""
        # Check blacklist paths
        if 'path' in tool_input:
            path = tool_input['path']
            for blacklisted in self.policies['BLACKLIST_PATHS']:
                if path.startswith(blacklisted):
                    return False

        # Check high-risk actions
        if any(action in tool_name.lower() or action in str(tool_input).lower() for action in self.policies['HIGH_RISK_ACTIONS']):
            return False  # Require confirmation

        return True

    def request_confirmation(self, message: str) -> bool:
        """Request verbal confirmation from user using TTS and speaker verification."""
        speak(message)
        audio, sr = record_command_audio(5)
        if verify_speaker(audio, sr):
            transcription = transcribe_audio(audio, sr)
            if 'yes' in transcription.lower() or 'confirm' in transcription.lower():
                return True
        return False

    def execute_tool(self, tool: Callable, tool_name: str, *args, **kwargs) -> Any:
        """Intercept and execute tool call with security checks."""
        tool_input = kwargs if kwargs else args[0] if args else {}
        if isinstance(tool_input, str):
            tool_input = {'query': tool_input}

        # Check for blacklist
        if 'path' in tool_input:
            path = tool_input['path']
            for blacklisted in self.policies['BLACKLIST_PATHS']:
                if path.startswith(blacklisted):
                    return "Policy violation: Action blocked."

        # Check for high-risk actions requiring confirmation
        if any(action in tool_name.lower() for action in self.policies['HIGH_RISK_ACTIONS']):
            if not self.request_confirmation(f"High-risk action: {tool_name}. Confirm by saying 'yes'."):
                return "Action rejected by user."

        # Execute the tool
        try:
            return tool(*args, **kwargs)
        except Exception as e:
            return f"Tool execution failed: {str(e)}"

# Global instance
security_mediator = SecurityMediator()