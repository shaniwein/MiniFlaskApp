import traceback, collections, contextlib, json, pika, time

default_host          = 'localhost'
default_port          = 5672
default_exchange_type = 'topic'

class Exchange:

    def __init__(self, mq, name, type=None, durable=None, auto_delete=None):
        self.mq          = mq
        self.name        = name
        self.type        = type or default_exchange_type
        self.durable     = durable
        self.auto_delete = auto_delete
        self.queues      = {}

    def create(self):
        self.mq._execute(lambda: self.mq.channel.exchange_declare(
            exchange      = self.name,
            exchange_type = self.type,
            durable       = self.durable,
            auto_delete   = self.auto_delete,
        ))
        return self 

    def delete(self, if_unused=None):
        self.mq._execute(lambda: self.mq.channel.exchange_delete(
            exchange  = self.name,
            if_unused = if_unused,
        ))
        return self

    def add_queue(self, queue):
        self.queues[queue.name] = queue

class Queue:

    def __init__(self, mq, name=None, durable=None, auto_delete=None, exclusive=None):
        self.mq          = mq
        self.name        = name        or ''
        self.durable     = durable     or False
        self.auto_delete = auto_delete or False
        self.exclusive   = exclusive   or False

    def create(self):
        result = self.mq._execute(lambda: self.mq.channel.queue_declare(
            queue       = self.name,
            durable     = self.durable,
            auto_delete = self.auto_delete,
            exclusive   = self.exclusive,
        ))
        self.name = result.method.queue
        return self
 
    def delete(self):
        self.mq._execute(lambda: self.mq.channel.queue_delete(
            queue = self.name,
        ))
        return self
    
    def bind(self, exchange, routing_key):
        self.mq._execute(lambda: self.mq.channel.queue_bind(
            exchange    = exchange.name,
            queue       = self.name,
            routing_key = routing_key,
        ))
        exchange.add_queue(self)
        return self

class MessageQueue:

    def __init__(self, host=None, port=None):
        self.host       = host or default_host
        self.port       = port or default_port
        self.connection = None
        self.channel    = None
        self._connect()

    def declare_exchange(self, name, type=None, durable=None, auto_delete=None):
        return Exchange(self, name, type, durable, auto_delete).create()
    
    def declare_queue(self, name=None, durable=None, auto_delete=None, exclusive=None, num=None):
        if num is None:
            return Queue(self, name, durable, auto_delete, exclusive).create()
        else:
            queues = []
            for i in range(num):
                queues.append(Queue(self, name, durable, auto_delete, exclusive).create())
            return queues

    def publish(self, exchange, routing_key, body):
        if isinstance(body, dict):
            body = json.dumps(body)
        if isinstance(body, str):
            body = body.encode()
        self._execute(lambda: self.channel.basic_publish(
            exchange    = exchange.name,
            routing_key = routing_key,
            body        = body, 
        ))
        return self
        
    def consume(self, exchange, queues, binding_keys, callback, no_ack=None):
        for queue in queues:
            for binding_key in binding_keys:
                queue.bind(exchange, binding_key)
            self._execute(lambda: self.channel.basic_consume(
                consumer_callback = callback,
                queue             = queue.name,
                no_ack            = no_ack,
            ))
            try:
                self._execute(lambda: self.channel.start_consuming())
            except KeyboardInterrupt:
                pass

    def _connect(self):
        self._close()
        while True:
            try:
                self.connection = pika.BlockingConnection(
                    parameters = pika.ConnectionParameters(
                        host = self.host,
                        port = self.port,
                    ),
                )
                self.channel = self.connection.channel()
                break
            except pika.exceptions.ConnectionClosed:
                time.sleep(0.1)

    def _close(self):
        if self.channel:
            with contextlib.suppress(pika.exceptions.ChannelClosed):
                self.channel.close()
        if self.connection:
            with contextlib.suppress(pika.exceptions.ConnectionClosed):
                self.connection.close()
        self.connection = self.channel = None

    def _execute(self, func):
        while True:
            try:
                return func()
            except pika.exceptions.ConnectionClosed:
                self._connect()
            except Exception:
                traceback.print_exc()
