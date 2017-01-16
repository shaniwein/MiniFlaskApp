import plugin

@plugin.matcher(['foo', 'bar'], 10)
def default_matcher(client):
    if client.name != 'hello':
        return True
    return False

@plugin.command('foo')
def foo_command(client):
    return 'print_foo'

@plugin.reactor('foo')
def foo_reactor(client):
    return 'publish foo'

@plugin.command('bar')
def bar_command(client):
    return 'print_bar'

@plugin.reactor('bar')
def bar_reactor(client):
    return 'publish bar'


@plugin.matcher(['x'], 5)
def special_matcher(client):
    if client.name == 'hey':
        return True
    return False

@plugin.command('x')
def x_command(client):
    return 'print_foo'

@plugin.reactor('x')
def x_reactor(client):
    return 'publish foo'

