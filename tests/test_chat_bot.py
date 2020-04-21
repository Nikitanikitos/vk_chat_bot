import logging
import unittest
from unittest.mock import patch, Mock, ANY

from vk_api.bot_longpoll import VkBotMessageEvent

from bot import Bot


class BotTest(unittest.TestCase):
    user_id = [
        {'id': 377158397, 'first_name': 'Иван', 'last_name': 'Петров', 'is_closed': True, 'can_access_closed': True}]
    raw_event_message_new = {'type': 'message_new',
                             'object': {
                                 'message': {'date': 1585408304, 'from_id': 377158397, 'id': 229, 'out': 0,
                                             'peer_id': 377158397, 'text': 'Зарегистрируй меня',
                                             'conversation_message_id': 218, 'fwd_messages': [], 'important': False,
                                             'random_id': 0, 'attachments': [], 'is_hidden': False},
                             },
                             'group_id': 193408079
                             }
    raw_event_message_replay = {'type': 'message_reply',
                                'object': {
                                    'date': 1585409090, 'from_id': -193408079, 'id': 235, 'out': 1,
                                    'peer_id': 377158397, 'text': 'Привет, Иван Петров!',
                                    'conversation_message_id': 224,
                                    'fwd_messages': [], 'important': False, 'random_id': 532962550, 'attachments': [],
                                    'is_hidden': False},
                                'group_id': 193408079,
                                }

    def setUp(self) -> None:
        self.count = 5
        self.obj = {}
        self.events = [self.obj] * self.count
        self.long_poller_mock = Mock(return_value=self.events)
        self.long_poller_listen_mock = Mock()
        self.long_poller_listen_mock.listen = self.long_poller_mock
        with patch("vk_chat_bot.vk_api.VkApi"):
            with patch("vk_chat_bot.VkBotLongPoll", return_value=self.long_poller_listen_mock):
                self.bot = Bot('', '')

    def test_run(self):
        self.bot.on_event = Mock()
        self.bot.run()
        self.bot.on_event.assert_called()
        self.bot.on_event.assert_any_call(self.obj)
        self.assertEqual(self.bot.on_event.call_count, self.count)

    def test_on_event_message_new(self):
        event = VkBotMessageEvent(raw=self.raw_event_message_new)
        send_mock = Mock()
        user_mock = Mock(return_value=self.user_id)
        self.bot.api = Mock()
        self.bot.api.messages.send = send_mock
        self.bot.api.users.get = user_mock
        self.bot.on_event(event)
        send_mock.assert_called_once_with(peer_id=self.raw_event_message_new['object']['message']['peer_id'],
                                          message='Использовать ваше имя Вконтакте или выбрать другое?',
                                          random_id=ANY)

    def test_on_event_message_replay(self):
        event = VkBotMessageEvent(raw=self.raw_event_message_replay)
        user_mock = Mock(return_value=self.user_id)
        self.bot.api = Mock()
        self.bot.api.users.get = user_mock
        self.bot.on_event(event)
        with self.assertLogs('stream_handler', level="INFO") as cm:
            logging.getLogger('stream_handler').info("Пользователю Иван Петров(id(377158397)) "
                                                     "отправлено сообщение 'Привет, Иван Петров!'")
            self.assertEqual(cm.output, [
                "INFO:stream_handler:Пользователю Иван Петров(id(377158397)) "
                "отправлено сообщение 'Привет, Иван Петров!'"])


if __name__ == '__main__':
    unittest.main()
