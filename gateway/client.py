import collections, requests, json, traceback

class Client:

    def __init__(self, properties):
        self.state = [] 
        self.__dict__.update(**properties)
    
    @classmethod
    def create(cls, data): # TODO: Add log
        try:
            client_properties = json.loads(data)
            return cls(client_properties)
        except Exception as e:
            raise ValueError # TODO: Handle exceptions at some level
    
    def update_state(self, tag, test=False):
        if isinstance(tag, list): # Updating from client side
            self.state = tag
        else:                     # Updating from app side
            self.state.append(tag) 
    
    def update_current(self, data):
        self.current = data.pop('command', None) 

    def post(self, url, result=None, data=None, dumps=False):
        if not data:
            data = self
        if result:
            data = {'result': result, **data.__dict__}
        if dumps:
            try:
                if isinstance(data, dict):
                    data = json.dumps(data)
                else:
                    data = json.dumps(data.__dict__)
            except:
                traceback.print_exc()
        return requests.post(url, data)
