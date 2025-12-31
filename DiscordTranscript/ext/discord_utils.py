class DiscordUtils:
    """A class containing utility strings for Discord.

    Attributes:
        logo (str): The URL of the Discord logo.
        default_avatar (str): The URL of the default Discord avatar.
        pinned_message_icon (str): The URL of the pinned message icon.
        thread_channel_icon (str): The URL of the thread channel icon.
        thread_remove_recipient (str): The URL of the thread remove recipient icon.
        thread_add_recipient (str): The URL of the thread add recipient icon.
        file_attachment_audio (str): The URL of the audio file attachment icon.
        file_attachment_acrobat (str): The URL of the acrobat file attachment icon.
        file_attachment_webcode (str): The URL of the webcode file attachment icon.
        file_attachment_code (str): The URL of the code file attachment icon.
        file_attachment_document (str): The URL of the document file attachment icon.
        file_attachment_archive (str): The URL of the archive file attachment icon.
        file_attachment_unknown (str): The URL of the unknown file attachment icon.
        button_external_link (str): The HTML for the button external link icon.
        reference_attachment_icon (str): The HTML for the reference attachment icon.
        interaction_command_icon (str): The HTML for the interaction command icon.
        interaction_dropdown_icon (str): The HTML for the interaction dropdown icon.
    """

    logo: str = (
        "https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-logo.svg"
    )
    default_avatar: str = (
        "https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-default.png"
    )
    pinned_message_icon: str = (
        "https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-pinned.svg"
    )
    thread_channel_icon: str = (
        "https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-thread.svg"
    )
    thread_remove_recipient: str = "https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-thread-remove-recipient.svg"
    thread_add_recipient: str = "https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-thread-add-recipient.svg"
    file_attachment_audio: str = (
        "https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-audio.svg"
    )
    file_attachment_acrobat: str = (
        "https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-acrobat.svg"
    )
    file_attachment_webcode: str = (
        "https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-webcode.svg"
    )
    file_attachment_code: str = (
        "https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-code.svg"
    )
    file_attachment_document: str = (
        "https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-document.svg"
    )
    file_attachment_archive: str = (
        "https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-archive.svg"
    )
    file_attachment_unknown: str = (
        "https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-unknown.svg"
    )
    button_external_link: str = '<img class="chatlog__reference-icon" src="https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-external-link.svg" alt="External link">'
    reference_attachment_icon: str = '<img class="chatlog__reference-icon" src="https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-attachment.svg" alt="Attachment">'
    interaction_command_icon: str = '<img class="chatlog__interaction-icon" src="https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-command.svg" alt="Slash Command">'
    interaction_dropdown_icon: str = '<img class="chatlog__dropdown-icon" src="https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-dropdown.svg" alt="Dropdown icon">'
    system_join_icon: str = "https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-thread-add-recipient.svg"
    system_boost_icon: str = "https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/discord-logo.svg"
