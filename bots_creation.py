from sessions_contoller import Session, Proxy
from opentele.td import TDesktop
from opentele.tl import TelegramClient
import exceptions
import time
from utils import acheck_proxy
from opentele.api import API, UseCurrentSession, CreateNewSession
from TGConvertor.manager.manager import SessionManager
from pyrogram import Client
import requests
from aiogram import Bot
import pyrogram.errors as pyrogram_errors
import string
import random
import settings
from pathlib import Path
import asyncio
import pyrogram


def make_username(bot_username_mask: str) -> str:
    username = bot_username_mask
    while '%' in username or '#' in username:
        username = username.replace('%', str(random.randint(0, 9)), 1)
        username = username.replace('#', random.choice(string.ascii_letters), 1)
    return username


def set_bot_description(bot_token: str, bot_description: str):
    url = f'https://api.telegram.org/bot{bot_token}/setMyDescription'
    data = {'description': bot_description}
    response = requests.get(url, json=data)
    return response


def set_bot_about(bot_token: str, bot_about: str):
    url = f'https://api.telegram.org/bot{bot_token}/setMyShortDescription'
    data = {'short_description': bot_about}
    response = requests.get(url, json=data)
    return response


async def create_bot(session: Session, bot_name: str, bot_username_mask: str, bot_description=None, bot_about=None, bot_image_path=None) -> dict:
    session_name = session.session_path.split('/')[-1].split('.')[0]
    print(f'Начата работа с сессией {session_name}')
    check = await acheck_proxy(proxy=session.proxy)
    if not check:
        print("Ошибка с прокси")
        raise exceptions.BadProxyError

    result = {
        'delay': None,
        'token': None,
        'username': None,
        'not_finshed': False
    }
    proxy = {
        'scheme': 'http',
        'hostname': session.proxy.ip,
        'port': session.proxy.port,
        'username': session.proxy.login,
        'password': session.proxy.password
    }
    try:
        api = API.TelegramAndroid.Generate()
        session = await SessionManager.from_telethon_file(Path(session.session_path), api=api)
        client = session.pyrogram_client(proxy=proxy)
    except Exception as e:
        print('----')
        print(e)
        print('----')
        raise exceptions.SessionError
    try:
        await client.start()
    except Exception as e:
        print(e)
        raise exceptions.BannedSessionError
    try:
        await client.get_chat('@BotFather')
        await client.send_message(chat_id=settings.botfather_id, text='/start')
        await client.send_message(chat_id=settings.botfather_id, text='/newbot')
    except Exception as e:
        print('----')
        print(e)
        print('----')
        raise exceptions.SessionError
    await asyncio.sleep(3)
    try:
        msg = [i async for i in client.get_chat_history(chat_id=settings.botfather_id, limit=1)][0]
    except Exception as e:
        print('----')
        print(e)
        print('----')
        raise exceptions.SessionError
    if msg.text.startswith('Sorry, too many attempts.'):
        time_delay = int(msg.text.split()[-2])
        result['delay'] = time_delay
        return result
    elif msg.text.startswith('Alright, a new bot.'):
        pass
    else:
        raise exceptions.NotFinishedSessionError
    try:
        await client.send_message(chat_id=settings.botfather_id, text=bot_name)
    except Exception as e:
        print('----')
        print(e)
        print('----')
        raise exceptions.SessionError
    try:
        msg = [i async for i in client.get_chat_history(chat_id=settings.botfather_id, limit=1)][0]
    except Exception as e:
        print('----')
        print(e)
        print('----')
        raise exceptions.SessionError
    if msg.text.startswith('Good.'):
        pass
    else:
        raise exceptions.NotFinishedSessionError

    msg_text = None
    while True:
        try:
            bot_username = make_username(bot_username_mask) + '_bot'
            await client.send_message(chat_id=settings.botfather_id, text=bot_username)
            await asyncio.sleep(3)
            msg = [i async for i in client.get_chat_history(chat_id=settings.botfather_id, limit=1)][0]
        except Exception as e:
            print('----')
            print(e)
            print('----')
            raise exceptions.SessionError
        if msg.text.startswith('Sorry,'):
            continue
        elif msg.text.startswith('Done!'):
            msg_text = msg.text
            break
        else:
            raise exceptions.NotFinishedSessionError
    if not msg_text:
        raise exceptions.NotFinishedSessionError
    token = msg_text.split('\n')[3]
    result['token'] = token
    result['username'] = bot_username
    try:
        if bot_description:
            response = set_bot_description(token, bot_description)
        if bot_about:
            response = set_bot_about(token, bot_about)
        if bot_image_path:
            await client.send_message(settings.botfather_id, '/setuserpic')
            await asyncio.sleep(2)
            await client.send_message(settings.botfather_id, '@' + bot_username)
            await asyncio.sleep(2)
            await client.send_photo(settings.botfather_id, bot_image_path)
    except Exception as e:
        print(e)
        result['not_finshed'] = True
    await client.stop()
    print(f'Закончена работа с сессией {session_name}')
    return result


