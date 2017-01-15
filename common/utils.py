class Dictionary:

    def __init__(self,response):
        self._response = response

    def __getattr__(self,key):
        try:
            return self._response[key]
        except KeyError:
            raise AttributeError(key)
