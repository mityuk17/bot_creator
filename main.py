import asyncio
import random
import exceptions
from utils import *
from sessions_contoller import Sessions_Contoller, Session, Proxy
import threading
from bots_creation import create_bot


def run_thread_work(sessions, session_controller, bot_info):
    asyncio.run(thread_work(sessions, session_controller, bot_info))


def write_data(thread_name, result):
    with open(f'result/tokens.txt', 'a') as file:
        file.write('\n'.join([i.split()[1] for i in result]))
        file.write('\n')
    with open(f'result/tokens_{thread_name}.txt', 'w') as file:
        file.write('\n'.join([i.split()[1] for i in result]))
    with open(f'result/urls.txt', 'a') as file:
        file.write('\n'.join([i.split()[0] for i in result]))
        file.write('\n')
    with open(f'result/urls_{thread_name}.txt', 'w') as file:
        file.write('\n'.join([i.split()[0] for i in result]))
    with open(f'result/result_{thread_name}.txt', 'w') as file:
        file.write('\n'.join(result))
    with open('result/result.txt', 'a') as file:
        file.write('\n'.join(result))
        file.write('\n')


async def thread_work(sessions: list[Session], session_controller: Sessions_Contoller, bot_info):
    thread_name = threading.current_thread().name
    print(f'Поток {thread_name} начал работу')
    result = list()
    name = bot_info.get('name')
    image_path = bot_info.get('image_path')
    description = bot_info.get('description')
    about = bot_info.get('about')
    username_mask = bot_info.get('username_mask')
    bots_amount = bot_info.get('bots_amount')
    while sessions:
        session = sessions[-1]
        session_name = session.session_path.split('/')[-1].split('.')[0]
        try:
            if session.bots_created == bots_amount:
                sessions.remove(session)
                continue
            response = await create_bot(session, name, username_mask, description, about, image_path)
            delay = response.get('delay')
            if delay:
                print(f'У сессии {session_name} таймаут: {delay}')
                if delay > 60 * 60:
                    sessions.remove(session)
                continue
            token = response.get('token')
            username = response.get('username')
            if token and username:
                result.append({'token': token,
                               'username': username})
                print(result[-1])
            sessions[-1].bots_created += 1
            sessions = [sessions[-1]] + sessions[:-1]
        except exceptions.SessionError as e:
            session_controller.session_error(session)
            sessions.remove(session)
            print(e)
        except exceptions.NotFinishedSessionError as e:
            session_controller.session_not_finished(session)
            sessions.remove(session)
            print(e)
        except exceptions.BannedSessionError as e:
            session_controller.session_banned(session)
            sessions.remove(session)
            print(e)
        except exceptions.BadProxyError as e:
            session.proxy = random.choice(session_controller.get_proxies())
            print(e)
        except Exception as e:
            session_controller.session_error(session)
            sessions.remove(session)
            print(e)
    for i in range(len(result)):
        url = f'''t.me/{result[i].get('username')}'''
        result[i] = f'''{url} {result[i].get('token')}'''
    write_data(thread_name, result)
    print(f'Поток {thread_name} закончил работу')


def main():
    image_path = get_image_path()
    description = get_bot_description()
    about = get_bot_about()
    username_mask = get_bot_username_mask()
    if not username_mask:
        print('Bot username_mask not found')
        return
    name = get_bot_name()
    if not name:
        print('Bot name not found')
        return
    controller = Sessions_Contoller()
    threads_amount = get_threads_amount()
    bots_amount = get_bots_amount()
    sessions = controller.get_sessions(threads_amount=threads_amount)
    bot_info = {
        'name': name,
        'image_path': image_path,
        'description': description,
        'about': about,
        'username_mask': username_mask,
        'bots_amount': bots_amount
    }
    for th in range(threads_amount):
        thread = threading.Thread(target=run_thread_work, args=[sessions[th], controller, bot_info])
        thread.start()
    while True:
        pass


if __name__ == '__main__':
    main()




