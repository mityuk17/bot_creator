
import aiohttp
import requests
import os
from sessions_contoller import Proxy
import socket


def valid_ip(address):
    try:
        socket.inet_aton(address)
        return True
    except:
        return False


def check_proxy(proxy: dict) -> bool:
    scheme = proxy.get('scheme')
    host = proxy.get('hostname')
    port = proxy.get('port')
    username = proxy.get('username')
    password = proxy.get('password')
    proxy_f = f'{scheme}://{username}:{password}@{host}:{port}'
    proxies = {
        'http': proxy_f,
        'https': proxy_f
    }
    original_ip = requests.get('https://api.ipify.org').text
    try:
        masked_ip = requests.get('https://api.ipify.org', proxies=proxies).text
    except requests.exceptions.ConnectionError:
        return False
    return masked_ip and original_ip != masked_ip


async def acheck_proxy(proxy: Proxy) -> bool:
    scheme = proxy.scheme
    host = proxy.ip
    port = proxy.port
    username = proxy.login
    password = proxy.password
    proxy_url = f'{scheme}://{username}:{password}@{host}:{port}'
    check_ip_url = 'http://api.ipify.org'
    session = aiohttp.ClientSession()
    try:
        async with session.get(url=check_ip_url) as response:
            original_ip = await response.text()
        async with session.get(url=check_ip_url, proxy=proxy_url) as response:
            masked_ip = await response.text()
    except Exception as e:
        print(e)
        return False
    await session.close()
    exp = valid_ip(masked_ip) and (masked_ip != original_ip)
    return exp


def get_image_path() -> str:
    files = os.listdir('photo')
    for file in files:
        if file.endswith('.jpg') or file.endswith('.png'):
            return 'photo/' + file
    return None


def get_bot_about() -> str:
    if os.path.exists('about.txt'):
        with open('about.txt', 'r', encoding='utf8') as file:
            about = file.readline()
            if about:
                return about
    return None


def get_bot_description() -> str:
    if os.path.exists('description.txt'):
        with open('description.txt', 'r', encoding='utf8') as file:
            description = file.readline()
            if description:
                return description
    return None


def get_bot_name() -> str:
    if os.path.exists('name.txt'):
        with open('name.txt', encoding='utf8') as file:
            name = file.readline()
            if name:
                return name
    else:
        return None


def get_threads_amount() -> int:
    num_threads = input('Введите количество потоков для работы:')
    while not num_threads.isdigit():
        num_threads = input('Введите количество потоков для работы:')
    return int(num_threads)


def get_bots_amount() -> int:
    num_bots = input('Введите количество ботов для создания на каждом аккаунте')
    while not num_bots.isdigit():
        num_bots = input('Введите количество ботов для создания на каждом аккаунте')
    return int(num_bots)


def get_bot_username_mask() -> str:
    if os.path.exists('username.txt'):
        with open('username.txt') as file:
            username = file.readline()
            if username:
                return username
    return None