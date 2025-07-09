"""Exception module."""

class VoiceAgentException(Exception):
    """Base exception for voice agent."""
    pass


class PromptNotFoundException(VoiceAgentException):
    """Prompt not found exception."""
    pass
