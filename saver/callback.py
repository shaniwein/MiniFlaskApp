import django, json, os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saver.settings")
django.setup()
from website.models import Client, Command, Result

from config import config

class Callback:

    def __init__(self, ch, method, properties, body):
        self.ch         = ch
        self.method     = method
        self.properties = properties
        self.body       = body
        self._validate()
    
    @classmethod
    def act(cls, ch, method, properties, body):
        callback = cls(ch, method, properties, body)
        callback.function(callback._parse(body))

    @property
    def model(self):
        return self.method.routing_key.split('.')[0]

    @property
    def action(self):
        return self.method.routing_key.split('.')[1]
    
    @property
    def function(self):
        return defined_functions[self.action] # TODO: Do I even need topics? Not using model
   
    def _validate(self):
        if not len(self.method.routing_key.split('.')) == config.mq.num_topic_nodes:
            raise ValueError('Routing key must have {num} topic nodes.'.format(num=config.mq.num_topic_nodes))
        if not self._decode_body():
            raise ValueError('Body must be utf8, not {value}.'.format(value=type(self.body)))
        try:
            json.loads(self.body.decode())
        except Exception:
            raise ValueError('Body must be a json dumps string.')
        for func in defined_functions.values(): 
            validate_key = getattr(func, 'validate_key', None) # Change to validate keys!
            if validate_key:
                try:
                    func_dict = json.loads(self.body.decode())
                    json.loads(self.body.decode())[validate_key]
                except Exception:
                    import traceback
                    traceback.print_exc()
                    raise ValueError('Body must contain {key} key for function {name}.'.format(key=validate_key, name=func.func_name))

    def _decode_body(self):
        try: 
            self.body.decode()
            return True
        except:
            return False
    
    def _parse(self, data):
        data = data.decode()
        try:
            return json.loads(data)
        except:
            return data

def client(func):
    def func_wrapper(data):
        func_wrapper.func_name = 'client'
        func_wrapper.validate_key = 'name' 
        func_wrapper.name = data['name'] 
        return func(data)
    return func_wrapper

def command(func):
    def func_wrapper(data):
        func_wrapper.func_name = 'command'
        #func_wrapper.validate_key = 'data'
        command_data = data['data']
        func_wrapper.name = command_data['command'] if command_data.get('command') else 'sleep'
        return func(data)
    return func_wrapper

def result(func):
    def func_wrapper(data):
        func_wrapper.func_name = 'result'
        func_wrapper.validate_key = 'data'
        func_wrapper.data = data['data'] 
        return func(data)
    return func_wrapper

@client
def new_client(data):
    client = Client(name=new_client.name)
    client.save()
    print('Inserted new client {name} to db.'.format(name=client.name))

@client
def session(data):
    client = Client.objects.get(
        name = session.name
    )
    client.update_last_connected()
    print('Updated client {name} last connected time.'.format(name=client.name))

@command
def new_command(data):
    client_id = Client.objects.get(name=data.get('name')).pk
    command = Command(client_id=client_id, name=new_command.name)
    command.save()
    print('Inserted new command {name} to db.'.format(name=command.name))

@result
def save_result(data):
    print('in result', data) 

defined_functions = dict(
    new     = new_client,
    session = session,
    command = new_command,
    save    = save_result,
)

