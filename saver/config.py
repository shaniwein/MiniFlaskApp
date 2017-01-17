import logging

from common.utils import Dictionary

config = Dictionary(dict(
    
    log = Dictionary(dict(  
        path = '/var/log/project/app.log',
    )),

    mq = Dictionary(dict(
        exchange_name = 'saver',
        num_topic_nodes = 2,  
    )),

))


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(config.log.path)
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)


