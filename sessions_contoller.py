import os
from dataclasses import dataclass

@dataclass
class Proxy:
    ip: str
    port: int
    login: str
    password: str
    scheme: str = 'http'
@dataclass
class Session:
    session_path: str
    proxy: Proxy
    bots_created: int = 0
    timeout: int = 0


class Sessions_Contoller():
    def __init__(self, sessions_path=os.getcwd()+'/accounts'):
        self.directories = ['banned', 'errored', 'executed', 'not_finished', 'source']
        self.sessions_directory = sessions_path
        if not os.path.exists(self.sessions_directory):
            raise FileNotFoundError('''Directory 'accounts' not found''')
        if not os.path.exists(self.sessions_directory+ '/source'):
            raise FileNotFoundError('''Directory 'source' not found''')
        if not os.listdir(self.sessions_directory + '/source'):
            raise FileNotFoundError('''No files in 'source' directory''')
        for directory in self.directories:
            if not os.path.exists(self.sessions_directory + f'/{directory}'):
                os.mkdir(self.sessions_directory + f'/{directory}')
        print('Sessions_controller is ready')

    @staticmethod
    def get_proxies() -> list[Proxy]:
        proxies = list()
        with open('proxies.txt', 'r') as file:
            data = file.readlines()
        for proxy_index in range(len(data)):
            proxy_data = data[proxy_index].strip().split(':')
            address = proxy_data[0]
            port = int(proxy_data[1])
            login = proxy_data[2]
            password = proxy_data[3]
            proxy = Proxy(address, port, login, password)
            proxies.append(proxy)
        return proxies

    def get_sessions(self, threads_amount: int) -> list[list[Session]]:
        proxies = self.get_proxies()
        sessions_paths = [file_name for file_name in os.listdir(self.sessions_directory+'/source') if file_name.endswith('.session')]
        thread_index_cursor = 0
        proxy_index_cursor = 0
        sessions_by_threads = [list() for _ in range(threads_amount)]
        while sessions_paths:
            session = Session(f'{self.sessions_directory}/source/{sessions_paths.pop()}', proxies[proxy_index_cursor])
            proxy_index_cursor = proxy_index_cursor + 1 if proxy_index_cursor < len(proxies)-1 else 0
            sessions_by_threads[thread_index_cursor].append(session)
            thread_index_cursor = thread_index_cursor + 1 if thread_index_cursor < threads_amount-1 else 0
        return sessions_by_threads

    def session_not_finished(self, session: Session):
        session_name = session.session_path.split('/')[-1].split('.')[0]
        os.replace(session.session_path, f'{self.sessions_directory}/not_finished/{session_name}.session')
        os.replace(f'{self.sessions_directory}/source/{session_name}.json', f'{self.sessions_directory}/not_finished/{session_name}.json')

    def session_banned(self, session: Session):
        session_name = session.session_path.split('/')[-1].split('.')[0]
        os.replace(session.session_path, f'{self.sessions_directory}/banned/{session_name}.session')
        os.replace(f'{self.sessions_directory}/source/{session_name}.json',
                   f'{self.sessions_directory}/banned/{session_name}.json')

    def session_error(self, session: Session):
        session_name = session.session_path.split('/')[-1].split('.')[0]
        os.replace(session.session_path, f'{self.sessions_directory}/errored/{session_name}.session')
        os.replace(f'{self.sessions_directory}/source/{session_name}.json',
                   f'{self.sessions_directory}/errored/{session_name}.json')

    def session_executed(self, session: Session):
        session_name = session.session_path.split('/')[-1].split('.')[0]
        os.replace(session.session_path, f'{self.sessions_directory}/executed/{session_name}.session')
        os.replace(f'{self.sessions_directory}/source/{session_name}.json',
                   f'{self.sessions_directory}/executed/{session_name}.json')
