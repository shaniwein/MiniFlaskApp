import collections, json, traceback

from client               import Client
from config               import config, logger
from plugin               import Plugin
from common.message_queue import MessageQueue

Response = collections.namedtuple('Response', 'data status_code')

response_types = dict(
    command = lambda x, client: Response(data=dict(command=x, state=client.state), status_code=200),
    sleep   = lambda x, client: Response(data=dict(sleep=x, state=client.state), status_code=303),
)

class Session:

    def __init__(self, data):
        self.data   = data
        self.client = Client(data)
        self.plugin = Plugin.load(config.plugins.plugins_path)
        self.mq     = MessageQueue(host='mq')
    
    def handle_new_session(self):
        try:
            if self.client.is_new:
                logger.info('New client {name} connected'.format(name=self.client.name))
                routing_key = 'client.new'
            else:       
                logger.info('Client {name} started new session'.format(name=self.client.name))
                routing_key = 'client.session'    
            self.mq.publish(
                exchange    = self.mq.declare_exchange('clients'),
                routing_key = routing_key,
                body        = self.client.properties,
            )
            return self.generate_response()
        except Exception as e:
            traceback.print_exc()
            logger.error('Failed handling new client. {e}'.format(e=e))
            
    def handle_submit(self):
        try:
            logger.info('Submission by client {name}'.format(name=self.client.name))
            if self.get_current():
                result = self.call_reactor()
                self.mq.publish(
                    exchange    = self.mq.declare_exchange('products'),
                    routing_key = 'product.{plugin}'.format(plugin=self.plugin.name),
                    body        = {'client': self.client.properties, 'result': result},
                )
            return self.generate_response()
        except Exception as e:
            traceback.print_exc()
            logger.error('Failed handling client submission. {e}'.format(e=e))
 
    def get_next_command(self):
        return self.client.get_next_command_by_state(self.plugin) 

    def call_reactor(self):
        tag = self.get_current()
        for reactor in self.plugin.reactors:
            if reactor.tag == tag:
                logger.debug('Passing client {name} submission to {reactor} reactor.'.format(name=self.client.name, reactor=reactor.tag))
                return reactor(self.client)
        
    def generate_response(self):
        command = self.get_next_command()
        response_type = 'command' if command else 'sleep'
        value = command.tag if command else config.client.default_sleep
        response = response_types[response_type](value, self.client)
        return json.dumps(response.data), response.status_code
        
    def get_current(self):
        try:
            data = json.loads(self.data)
        except:
            data = self.data
        return data.pop('current', None)
