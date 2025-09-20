import unittest
import asyncio
from unittest.mock import patch, Mock, MagicMock
import discord
from src.discord_html_transcripts.main import create_transcript

class TestTranscripts(unittest.TestCase):

    def setUp(self):
        # Mock Channel
        self.mock_channel = MagicMock(spec=discord.TextChannel)
        self.mock_channel.name = "test-channel"
        self.mock_channel.topic = "Test Topic"
        self.mock_channel.guild = MagicMock(spec=discord.Guild)
        self.mock_channel.guild.name = "Test Guild"

        # Mock Users
        self.mock_user1 = MagicMock(spec=discord.User)
        self.mock_user1.name = "User1"
        self.mock_user1.avatar_url = "https://via.placeholder.com/150"
        self.mock_user1.default_avatar_url = "https://via.placeholder.com/150"

        self.mock_user2 = MagicMock(spec=discord.User)
        self.mock_user2.name = "User2"
        self.mock_user2.avatar_url = "https://via.placeholder.com/150"
        self.mock_user2.default_avatar_url = "https://via.placeholder.com/150"

        # Mock Messages
        self.mock_message1 = MagicMock(spec=discord.Message)
        self.mock_message1.author = self.mock_user1
        self.mock_message1.content = "Hello"
        self.mock_message1.created_at.strftime.return_value = "2025-01-01 00:00:00"
        self.mock_message1.is_system.return_value = False
        self.mock_message1.reference = None
        self.mock_message1.attachments = []
        self.mock_message1.embeds = []
        self.mock_message1.reactions = []

        self.mock_message2 = MagicMock(spec=discord.Message)
        self.mock_message2.author = self.mock_user2
        self.mock_message2.content = "Hi there!"
        self.mock_message2.created_at.strftime.return_value = "2025-01-01 00:01:00"
        self.mock_message2.is_system.return_value = False
        self.mock_message2.reference = None
        self.mock_message2.attachments = []
        self.mock_message2.embeds = []
        self.mock_message2.reactions = []

        self.messages = [self.mock_message1, self.mock_message2]

        async def history(limit=None):
            return self.messages

        self.mock_channel.history.return_value = MagicMock()
        self.mock_channel.history.return_value.flatten = history


    def test_create_transcript(self):
        async def run_test():
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.content = b'fake image data'
                mock_get.return_value = mock_response

                html = await create_transcript(self.mock_channel)
                self.assertIsInstance(html, str)
                self.assertIn("</html>", html)
                self.assertIn("Test Guild", html)
                self.assertIn("#test-channel", html)
                self.assertIn("User1", html)
                self.assertIn("User2", html)
                self.assertIn("Hello", html)
                self.assertIn("Hi there!", html)

        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()
