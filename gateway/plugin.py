import collections, os, importlib.util, traceback

from config import config, logger

plugins_cache = {}

CachedPlugin  = collections.namedtuple('CachedPlugin', 'plugin last_modification_time')

def matcher(func):
    func._matcher = True
    return func

def command(tag, priority):
    def decorated_command(func):
        func._command = True
        func.tag      = tag
        func.priority = priority
        return func
    return decorated_command

def reactor(tag):
    def decorated_reactor(func):
        func._reactor = True
        func.tag = tag
        return func
    return decorated_reactor

class Plugin:

    def __init__(self, path, name, module):
        self.path     = path
        self.name     = name
        self.module   = module
        self.matchers = self.find_items('_matcher')
        self.commands = self.find_items('_command')
        self.reactors = self.find_items('_reactor')

    @classmethod
    def load(cls, path, name=None):
        if not name:
            name = os.path.splitext(os.path.basename(path))[0]
        last_modification_time = os.stat(path).st_mtime
        if path not in plugins_cache or plugins_cache[path].last_modification_time < last_modification_time:
            # TODO: use load_from_source
            spec        = importlib.util.spec_from_file_location(name, path)
            module      = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                plugin = cls(
                    path     = path,
                    name     = name,
                    module   = module,
                )
                if not cls.validate_plugin(plugin):
                    raise ValueError
            except:
                plugin = None
                traceback.print_exc()
            plugins_cache[path] = CachedPlugin(plugin, last_modification_time)
        return plugins_cache[path].plugin
    
    @property
    def priority(self):
        return getattr(self.module, 'priority', config.plugins.default_priority)

    def find_items(self, item):
        items = []
        for key, value in self.module.__dict__.items():
            if hasattr(value, item):
                items.append(value)
        return items

    def validate_plugin(self): # TODO: Add log
        if len(self.matchers) != 1:
            logger.error('Plugin must define one matcher ({num} defined).'.format(num=len(self.matchers)))
            return False
        if not self.commands:
            logger.error('Plugin must define at least one command.')
            return False
        if not self.reactors:
            logger.error('Plugin must define at least one reactor.')
            return False
        return True

