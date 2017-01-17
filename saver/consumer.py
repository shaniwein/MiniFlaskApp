import datetime, os, traceback, json

from config               import config
from common.message_queue import MessageQueue

def client(action, data):
    def new(body):
        client = Client.create(name=body.get('name'))
        client.save()
        print('Inserted new client {name} to db.'.format(name=client.name))
    def session(body):
        client = Client.objects.get(
            name = body.get('name')
        )
        client.update_last_connected()
        print('Updated client {name} last connected time.'.format(name=client.name))
    locals()[action](data)

def command(action, body):
    print('in command', action, body)

def result(action, body):
    print('in result', action, body) 

def parse(data):
    data = data.decode()
    try:
        return json.loads(data)
    except:
        return data
    
def callback(ch, method, properties, body):
    func, action = method.routing_key.split('.')
    globals()[func](action, parse(body))

def start_consuming():
    print('Starting consume...')
    mq       = MessageQueue('mq')
    exchange = mq.declare_exchange(config.mq.exchange_name)
    queue    = mq.declare_queue()
    mq.consume(exchange, queue, ['client.new', 'client.session', 'command.*', 'result.*'], callback)

if __name__ == "__main__":
    try:
        import django
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saver.settings")
        django.setup()
        from website.models import Client, Command, Result
        start_consuming()
    except Exception as e:
        traceback.print_exc()

