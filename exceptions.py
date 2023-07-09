class NotFinishedSessionError(Exception):
    pass


class SessionError(Exception):
    pass


class BannedSessionError(Exception):
    pass

class BadProxyError(Exception):
    pass