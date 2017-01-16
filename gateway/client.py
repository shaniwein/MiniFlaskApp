import collections, requests, json, traceback

from config import logger

class Client:

    def __init__(self, data):
        self.state      = []
        self.properties = json.loads(data)
        self.update_state()
    
    @property
    def name(self):
        return self.properties.get('name')    

    @property
    def is_new(self):
        return not self.state # If new, state is []
   
    def as_dict(self):
        return {**self.properties, 'state': self.state}
 
    def get_next_command_by_state(self, plugin):
        for command in sorted(plugin.commands, key=lambda x: x.priority, reverse=True):
            if command.tag in self.state:
                logger.debug('Client already got command {command}, continuing'.format(command=command.tag))
                continue
            for matcher in plugin.matchers:
                if matcher(self):
                    self.update_state(command.tag)
                    logger.debug('Client matched {plugin} matcher, returning command {command}'.format(plugin=plugin.name, command=command.tag))
                    return command
                logger.debug('Client did not match plugin {plugin}.'.format(plugin=plugin.name))

    def update_state(self, value=None, test=False):
        if isinstance(value, list): # Updating from client side
            self.state = value
        if isinstance(value, str):  # Updating from app side
            self.state.append(value)
        else:                       # Updating from received data
            received_state = self.properties.get('state')
            if received_state:
                self.state = received_state

    def update_current(self, data):
        self.current = data.pop('command', None) 

    def post(self, url, result=None, dumps=True):
        data = self
        if result:
            data = {'result': result, **data.as_dict()}
        if dumps:
            try:
                if isinstance(data, dict):
                    data = json.dumps(data)
                else:
                    data = json.dumps(data.as_dict())
            except:
                traceback.print_exc()
        return requests.post(url, data)
