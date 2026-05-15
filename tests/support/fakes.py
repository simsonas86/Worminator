class FakeBot:
    def __init__(self):
        self.pool = object()
        self.twitch = object()
        self.winners = []
        self.db_calls = []

    async def queue_db(self, func, *args):
        self.db_calls.append((func, args))
        return None


class FakeUser:
    def __init__(self, user_id=123, name="admin"):
        self.id = str(user_id)
        self.name = name


class FakeCommand:
    def __init__(self, user_id=123, name="admin", parameter=""):
        self.user = FakeUser(user_id, name)
        self.parameter = parameter
        self.replies = []

    async def reply(self, message):
        self.replies.append(message)


class FakeCloseablePool:
    def __init__(self):
        self.closed = False

    async def close(self):
        self.closed = True


class MessageRecorder:
    def __init__(self):
        self.messages = []

    async def __call__(self, message):
        self.messages.append(message)
