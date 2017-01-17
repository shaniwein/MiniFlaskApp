import datetime

class Dictionary(dict):

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

now = datetime.datetime.utcnow
