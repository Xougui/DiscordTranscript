async def discriminator(user: str, discriminator: str):
    """Formats a username and discriminator.

    Args:
        user (str): The username.
        discriminator (str): The discriminator.

    Returns:
        str: The formatted username and discriminator.
    """
    if discriminator != "0":
        return f"{user}#{discriminator}"
    return user