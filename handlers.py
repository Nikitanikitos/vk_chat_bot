
"""
Handler - функции-обработчики для получения имени и почты.
"""
import re
from io import BytesIO
from os import path
import requests
from PIL import Image, ImageFont, ImageDraw

R_NAME = re.compile(r'^[\w\-\s]{3,40}$')
R_EMAIL = re.compile(r'\b([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})\b')
TICKET_TEMPLATE = path.abspath(path.join('files', 'ticket_template.png'))
FONT = path.abspath(path.join('files', 'Roboto-Regular.ttf'))

def handler_name(text, context):
    match = re.match(R_NAME, text)
    if match:
        context['name'] = text
        return True
    return False

def handler_email(text, context):
    if re.match(R_EMAIL, text):
        context['mail'] = text
        return True
    return False

def handler_ticket(context):
    ticket = Image.open(TICKET_TEMPLATE)
    font = ImageFont.truetype(font=FONT, size=20)

    draw = ImageDraw.Draw(ticket)
    draw.text((220, 215), text=context['name'], font=font, fill=(0,0,0,255))
    draw.text((220, 255), text=context['mail'], font=font,fill=(0,0,0,255))
    response = requests.get(url=f"https://api.adorable.io/avatars/100/{context['mail']}.png")
    # TODO Вынести постоянную часть урла в константу

    avatar_file_like = BytesIO(response.content)
    avatar = Image.open(avatar_file_like)

    ticket.paste(avatar, (60, 190))

    temp_file = BytesIO()
    ticket.save(temp_file, 'png')
    temp_file.seek(0)
    return temp_file
# TODO Поправить код по требованиям РЕР8
