import plugin

@plugin.matcher
def matcher(client):
    if client.name != 'hello':
        return True
    return False

@plugin.command('foo', 10)
def foo_command(client):
    return 'print_foo'

@plugin.reactor('foo')
def foo_reactor(client):
    return 'publish foo'

@plugin.command('bar', 100)
def bar_command(client):
    return 'print_bar'

@plugin.reactor('bar')
def bar_reactor(client):
    return 'publish bar'

