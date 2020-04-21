import requests
from pony.orm import db_session

import handlers
import settings
from log_settings import file_handler, file_stream_handler, stream_handler
from models import UserState

try:
    from settings import TOKEN, GROUP_ID
except ImportError:
    exit("Do copy settings.py.default in settings.py and set TOKEN and GROUP_ID values")

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id


class Bot:
    """
    Echo bot для vk.com
    """
    def __init__(self, group_id, token):
        """

        :param group_id: id твоей группы Вк
        :param token: token твоей группы Вк
        """
        self.group_id = group_id
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        """
        Запуск Бота
        :return: None
        """
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except TypeError as arr:
                file_handler.exception(
                    f"Ошибка типа: {arr.__class__.__name__}\n\tКажется, я не умею обрабатывать запрос {event.type}...")

    @db_session
    def on_event(self, event):
        """
        Событие по обратоки ивентов
        :param event:
        :return: None
        """

        # получение id юзера
        user_id = self.get_user_id(event)
        # получение имени юзера
        get_user = self.api.users.get(user_id=user_id)[0]
        name_user = ' '.join([get_user['first_name'], get_user['last_name']])

        #       обработка ивента MESSAGE_NEW
        if event.type == VkBotEventType.MESSAGE_NEW:
            state = UserState.get(user_id=user_id)
            text = event.message['text'].lower()
            if state:
               self.continue_scenario(text, state)
            else:
                for intent in settings.INTENTS:
                    if any(token in text.lower() for token in intent['tokens']):
                        if intent['answer']:
                            self.send_text(text_to_send=intent['answer'].format(name=name_user), user_id=user_id)
                        else:
                            self.start_scenario(intent, intent['scenario'], user_id, name_user)
                        break
                else:
                    self.send_text(text_to_send=settings.DEFAULT_MESSAGE, user_id=user_id)
            file_stream_handler.info(
                f"Пришлое новое сообщение от пользователя {name_user}(id({user_id})): {text}")


        elif event.type == VkBotEventType.MESSAGE_REPLY:
            file_stream_handler.info(
                f"Пользователю {name_user}(id({user_id})) отправлено сообщение '{event.object.text}'")
        else:
            stream_handler.info(f"Получено событие {event.type}, c которым я не умею работать")
            raise TypeError

    def get_user_id(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.message['from_id']
        elif event.type == VkBotEventType.MESSAGE_REPLY:
            user_id = event.object.peer_id
        else:
            user_id = event.obj.from_id
        return user_id

    def start_scenario(self, intent,  scenario_name, user_id, name_user):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = intent['first_step']
        step = scenario['steps'][first_step]
        state = UserState(user_id=user_id, scenario_name=scenario_name,
                          step_name=first_step, context={'name':name_user})
        self.send_data(state=state, text_to_send=step['text'])

    def continue_scenario(self, text, state):
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler'])
        if handler(text, state.context):
            state.step_name = step['next_step']
            next_step = steps[step['next_step']]
            self.send_data(state=state, text_to_send=next_step['text'].format(**state.context))
            if next_step['next_step']:
                state.step_name = step['next_step']
            else:
                state.delete()
        else:
            self.send_data(state=state, text_to_send=step['failure_text'].format(**state.context))

    def send_ticket(self, state, ticket):
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(url=upload_url, files={'photo': ('ticket.png', ticket, 'ticket/png')}).json()
        save_ticket = self.api.photos.saveMessagesPhoto(**upload_data)

        owner_id = save_ticket[0]['owner_id']
        media_id = save_ticket[0]['id']
        attachment = f'photo{owner_id}_{media_id}'
        self.api.messages.send(peer_id=state.user_id, attachment=attachment, random_id=get_random_id())

    def send_text(self, text_to_send, user_id):
        self.api.messages.send(peer_id=user_id, message=text_to_send, random_id=get_random_id())

    def send_data(self, text_to_send, state):
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        if 'image' in step:
            handler = getattr(handlers, step['image'])
            ticket = handler(state.context)
            self.send_ticket(ticket=ticket, state=state)
        self.send_text(text_to_send, state.user_id)

if __name__ == '__main__':
    bot = Bot(GROUP_ID, TOKEN)
    bot.run()

# зачет!
