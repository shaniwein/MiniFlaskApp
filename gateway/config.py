import logging

from common.utils import Dictionary

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('/var/log/project/app.log')
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)


config = Dictionary(dict(
    
    app = Dictionary(dict(
        connect_url = 'http://127.0.0.1:5000/connect',
        submit_url  = 'http://127.0.0.1:5000/submit',
    )),

    mq = Dictionary(dict(
        default_host = 'localhost',
        default_port = 5672,
        default_exchange_name = '',
        default_exchange_type = 'topic',
    )),

    plugins = Dictionary(dict(
        plugins_path     = '/home/user/course/project/gateway/run_plugins.py',
        default_priority = 0,
    )),
    
    client = Dictionary(dict(
        default_sleep = 10,
    )),

))
