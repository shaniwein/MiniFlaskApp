import traceback, collections, contextlib, json, pika, time

Exchange = collections.namedtuple('Exchange', 'name object')
Queue    = collections.namedtuple('Queue', 'name object')

default_host = 'localhost'
default_port = 5672
default_exchange_name = ''
default_exchange_type = 'topic'

class MessageQueue:

    def __init__(self, host=None, port=None):
        self.host       = host or default_host
        self.port       = port or default_port
        self.connection = None
        self.channel    = None
        self.exchange   = None
        self._connect()

    def declare_exchange(self, name=None, type=None):
        name = name or default_exchange_name
        type = type or default_exchange_type       
        self.exchange = Exchange(
            name   = name,
            object = self._execute(lambda: self.channel.exchange_declare(
                exchange = name,
                type     = type,
            )
        ))
        return self
    
    def declare_queue(self, name, durable=None, auto_delete=None, exclusive=None):
        self.queue = Queue(
            name   = name,
            object = self._execute(lambda: self.channel.queue_declare(
                queue = name,
                durable = durable,
                auto_delete = auto_delete,
                exclusive = exclusive,
            )
        ))
        return self
    
    def bind_queue(self, routing_key, exchange=None):
        self._execute(lambda: self.message_queue.channel.queue_bind(
            exchange    = exchange or self.exchange.name,
            queue       = self.queue.name,
            routing_key = routing_key,
        ))
        return self

    def publish(self, routing_key, body):
        if not self.exchange:
            self.declare_exchange()
        if isinstance(body, dict):
            body = json.dumps(body)
        if isinstance(body, str):
            body = body.encode()
        self._execute(lambda: self.channel.basic_publish(
            exchange    = self.exchange.name,
            routing_key = routing_key,
            body        = body, 
        ))
        return self
        
    def consume(self, exchange, queue_name, binding_keys, callback, no_ack=None):
        self.declare_queue(queue_name)
        for binding_key in list(binding_keys):
            self.channel.queue_bind(
                exchange    = exchange.name,
                queue       = self.queue.name,
                routing_key = binding_key,
            )
        self._execute(lambda: self.channel.basic_consume(
            consumer_callback = callback,
            queue             = self.queue.name,
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
            except:
                traceback.print_exc()
