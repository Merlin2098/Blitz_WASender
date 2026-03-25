import unittest

from src.infrastructure.whatsapp_web.locators import (
    MESSAGE_COMPOSER_LOCATORS,
    OPEN_CHAT_LOCATORS,
    SEND_BUTTON_LOCATORS,
    SESSION_ACTIVE_LOCATORS,
)


class WhatsAppLocatorTests(unittest.TestCase):
    def test_session_locators_include_sidebar_signal(self):
        self.assertIn(("css selector", "#pane-side"), SESSION_ACTIVE_LOCATORS)

    def test_message_composer_locators_cover_current_dom_and_legacy_fallback(self):
        composer_values = {value for _, value in MESSAGE_COMPOSER_LOCATORS}
        self.assertTrue(any("Escribir un mensaje" in value for value in composer_values))
        self.assertTrue(any("@data-tab='10'" in value for value in composer_values))

    def test_open_chat_locators_cover_main_chat_shell(self):
        self.assertIn(("css selector", "#main"), OPEN_CHAT_LOCATORS)
        self.assertIn(("css selector", "#main footer"), OPEN_CHAT_LOCATORS)

    def test_send_button_locator_targets_send_not_audio(self):
        self.assertEqual(len(SEND_BUTTON_LOCATORS), 1)
        strategy, value = SEND_BUTTON_LOCATORS[0]
        self.assertEqual(strategy, "xpath")
        self.assertIn("@aria-label='Enviar'", value)
        self.assertNotIn("audio", value.lower())


if __name__ == "__main__":
    unittest.main()
