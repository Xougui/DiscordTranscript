import pytest

from DiscordTranscript.construct.assets.attachment import Attachment


class DummyAttachment:
    def __init__(
        self,
        filename,
        content_type="text/plain",
        size=1024,
        text=None,
        url="https://example.com/test.txt",
    ):
        self.filename = filename
        self.content_type = content_type
        self.size = size
        self.text = text
        self.url = url
        self.proxy_url = url


@pytest.mark.asyncio
async def test_text_attachment_preview():
    att = DummyAttachment(
        "test.txt", "text/plain", 1024, text="Ceci est un test de contenu textuel."
    )
    attachment_obj = Attachment(att, None, language="fr")
    html = await attachment_obj.flow()
    assert "chatlog__attachment-text-container" in html
    assert "test.txt" in html
    assert "Ceci est un test de contenu textuel." in html
    assert "1 Ko" in html
    assert "chatlog__attachment-text-toggle" in html


@pytest.mark.asyncio
async def test_non_text_attachment():
    att = DummyAttachment("archive.zip", "application/zip", 2048)
    attachment_obj = Attachment(att, None, language="fr")
    html = await attachment_obj.flow()
    assert "chatlog__attachment-container" in html
    assert "chatlog__attachment-text-container" not in html
