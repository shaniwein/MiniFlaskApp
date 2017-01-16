import collections, sys, requests, json, random, time, traceback

from client import Client
from config import config

Response = collections.namedtuple('Response', 'data status_code state')

def print_foo():
    return 'foo'

def print_bar():
    return 'bar'

def run_command(response):
    try:
        command = response.data['command']
        print('command', command)
        return command_mapping[command]()
    except Exception:
        print('Command {name} is not defined in client.'.format(name=command))

def sleep(response):
    seconds = int(response.data['sleep'])
    print('Sleeping for {num} seconds.'.format(num=seconds))
    time.sleep(seconds)
 
status_code_mapping = {
    '200': run_command,
    '303': sleep,
}

command_mapping = {
    'foo': print_foo,
    'bar': print_bar,
    'x'  : print_foo,
}

def parse_response(response):
    text = json.loads(response.text)
    return Response(
        state       = text.pop('state'),
        data        = text,
        status_code = response.status_code,
    )

def run(name):
    client = Client(json.dumps(dict(name=name)))
    while True:
        try:
            response = parse_response(client.post(config.app.connect_url))
            result = status_code_mapping[str(response.status_code)](response)
            client.update_state(response.state)
            client.update_current(response.data)
            client.post(config.app.submit_url, result=result)
        except KeyboardInterrupt:
            break
        except:
            traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        client_name = sys.argv[1]
    else:
        import random
        client_name = str(random.randint(1, 1000))
    run(client_name)
