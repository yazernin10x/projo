from django.contrib.messages import get_messages


def assert_message_present(response, message, level_tag="success") -> None:
    """Vérifie si un message spécifique est présent dans les messages."""
    messages = list(get_messages(response.wsgi_request))
    assert any(
        msg.message == message and msg.level_tag == level_tag for msg in messages
    ), f"Message '{message}' avec level '{level_tag}' non trouvé"
