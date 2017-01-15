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
        self.client = Client.create(data)
        self.plugin = Plugin.load(config.plugins.plugin_path)
        self.mq     = MessageQueue(host='mq')
    
    def handle_new_session(self):
        try:
            self.mq.declare_exchange('clients')
            new_client = not self.client.state # If new, state is []
            if new_client:
                logger.info('New client {name} connected'.format(name=self.client.name))
                self.mq.publish(
                    routing_key = 'client.new',
                    body        = self.client.__dict__,
                )
            else:       
                logger.info('Client {name} started new session'.format(name=self.client.name))
                self.mq.publish(
                    routing_key = 'client.session',
                    body        = self.client.__dict__,
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
                self.mq.declare_exchange('products')
                self.mq.publish(
                    routing_key = 'product.{plugin}'.format(plugin=self.plugin.name),
                    body        = {'client': self.client.__dict__, 'result': result},
                )
            return self.generate_response()
        except Exception as e:
            traceback.print_exc()
            logger.error('Failed handling client submission. {e}'.format(e=e))
 
    def get_next_command(self):
        for command in sorted(self.plugin.commands, key=lambda x: x.priority, reverse=True):
            if command.tag in self.client.state:
                logger.debug('Client already got command {command}, continuing'.format(command=command.tag))
                continue
            for matcher in self.plugin.matchers:
                if matcher(self.client):
                    self.client.update_state(command.tag)
                    logger.debug('Client matched {plugin} metcher, returning command {command}'.format(plugin=self.plugin.name, command=command.tag))
                    return command
                logger.debug('Client did not match plugin {plugin}.'.format(plugin=self.plugin.name))

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
