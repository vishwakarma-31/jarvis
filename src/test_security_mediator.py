import unittest
from unittest.mock import patch, MagicMock
from security_mediator import SecurityMediator

class TestSecurityMediator(unittest.TestCase):
    def setUp(self):
        self.mediator = SecurityMediator()

    def test_check_policy_allowed(self):
        """Test policy check for allowed action."""
        result = self.mediator.check_policy("read_file", {"path": "/safe/path"})
        self.assertTrue(result)

    def test_check_policy_blacklist_blocked(self):
        """Test policy check for blacklisted path."""
        result = self.mediator.check_policy("delete_file", {"path": "C:/Windows/system32"})
        self.assertFalse(result)

    def test_check_policy_high_risk_blocked(self):
        """Test policy check for high-risk action."""
        result = self.mediator.check_policy("delete_tool", {"query": "delete something"})
        self.assertFalse(result)

    @patch('security_mediator.speak')
    @patch('security_mediator.record_command_audio')
    @patch('security_mediator.verify_speaker')
    @patch('security_mediator.transcribe_audio')
    def test_request_confirmation_yes(self, mock_transcribe, mock_verify, mock_record, mock_speak):
        """Test confirmation with 'yes' response."""
        mock_record.return_value = (MagicMock(), 16000)
        mock_verify.return_value = True
        mock_transcribe.return_value = "yes"
        result = self.mediator.request_confirmation("Test message")
        self.assertTrue(result)
        mock_speak.assert_called_once_with("Test message")

    @patch('security_mediator.speak')
    @patch('security_mediator.record_command_audio')
    @patch('security_mediator.verify_speaker')
    @patch('security_mediator.transcribe_audio')
    def test_request_confirmation_no(self, mock_transcribe, mock_verify, mock_record, mock_speak):
        """Test confirmation with 'no' response."""
        mock_record.return_value = (MagicMock(), 16000)
        mock_verify.return_value = True
        mock_transcribe.return_value = "no"
        result = self.mediator.request_confirmation("Test message")
        self.assertFalse(result)

    @patch('security_mediator.speak')
    @patch('security_mediator.record_command_audio')
    @patch('security_mediator.verify_speaker')
    @patch('security_mediator.transcribe_audio')
    def test_execute_tool_policy_violation(self, mock_transcribe, mock_verify, mock_record, mock_speak):
        """Test tool execution with policy violation."""
        mock_record.return_value = (MagicMock(), 16000)
        mock_verify.return_value = True
        mock_transcribe.return_value = "yes"
        mock_tool = MagicMock(return_value="success")
        result = self.mediator.execute_tool(mock_tool, "delete_tool", {"path": "C:/Windows"})
        self.assertEqual(result, "Policy violation: Action blocked.")
        mock_tool.assert_not_called()

    @patch('security_mediator.speak')
    @patch('security_mediator.record_command_audio')
    @patch('security_mediator.verify_speaker')
    @patch('security_mediator.transcribe_audio')
    def test_execute_tool_high_risk_confirmed(self, mock_transcribe, mock_verify, mock_record, mock_speak):
        """Test high-risk tool execution with confirmation."""
        mock_record.return_value = (MagicMock(), 16000)
        mock_verify.return_value = True
        mock_transcribe.return_value = "yes"
        mock_tool = MagicMock(return_value="deleted")
        result = self.mediator.execute_tool(mock_tool, "delete_tool", {"path": "/safe/path"})
        self.assertEqual(result, "deleted")
        mock_tool.assert_called_once_with({"path": "/safe/path"})

    @patch('security_mediator.speak')
    @patch('security_mediator.record_command_audio')
    @patch('security_mediator.verify_speaker')
    @patch('security_mediator.transcribe_audio')
    def test_execute_tool_high_risk_rejected(self, mock_transcribe, mock_verify, mock_record, mock_speak):
        """Test high-risk tool execution with rejection."""
        mock_record.return_value = (MagicMock(), 16000)
        mock_verify.return_value = True
        mock_transcribe.return_value = "no"
        mock_tool = MagicMock(return_value="deleted")
        result = self.mediator.execute_tool(mock_tool, "delete_tool", {"path": "/safe/path"})
        self.assertEqual(result, "Action rejected by user.")
        mock_tool.assert_not_called()

if __name__ == '__main__':
    unittest.main()