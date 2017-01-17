import os, traceback, json

from config               import config
from common.message_queue import MessageQueue
from callback             import Callback
    
def callback(ch, method, properties, body):
    Callback.act(ch, method, properties, body)
    
def start_consuming():
    print('Starting consume...')
    mq       = MessageQueue('mq')
    exchange = mq.declare_exchange(config.mq.exchange_name)
    queue    = mq.declare_queue()
    mq.consume(exchange, queue, ['client.new', 'client.session', 'command.*', 'result.*'], callback)

if __name__ == "__main__":
#    import django
#    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saver.settings")
#    django.setup()
#    from website.models import Client, Command, Result
    start_consuming()

