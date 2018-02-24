import argparse
import logging
import os
import sys

from pywebostv.connection import WebOSClient
from pywebostv.controls import (
    MediaControl, SystemControl, ApplicationControl, InputControl, SourceControl)
from pywebostv.config import get_config, save_config


def check_readable_file(filename):
    """Check the given argument is the filename of a readable file."""
    if not os.access(os.path.expanduser(filename), os.R_OK):
        raise argparse.ArgumentTypeError(
            '{} is not a readable file'.format(filename)
        )
    return os.path.expanduser(filename)


def parse_args(args=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='CLI for controlling LG TVs (Web OS).')

    parser.add_argument(
        '--config', '-c', default='~/.lgtv.json', type=check_readable_file,
        help='lgtv configuration (minimally ip, host and client-key)')

    subparsers = parser.add_subparsers()

    parsers = {
        'scan': {'defaults': {'control': WebOSClient, 'func': 'discover'}},
        'auth': {
            'defaults': {'control': WebOSClient, 'func': 'connect'},
            'arg': {'metavar': 'Hostname/IP'},
            'args': [{'flags': ['--output-config', '-o'], 'type': argparse.FileType('w'), 'default': sys.stdout}]},
        'audioVolume': {'defaults': {'control': MediaControl, 'func': 'get_volume'}},
        'volumeUp': {'defaults': {'control': MediaControl, 'func': 'volume_up'}},
        'volumeDown': {'defaults': {'control': MediaControl, 'func': 'volume_down'}},
        'setVolume': {
            'defaults': {'control': MediaControl, 'func': 'set_volume'},
            'arg': {'metavar': 'level', 'type': int}},
        'mute': {
            'defaults': {'control': MediaControl, 'func': 'mute'},
            'arg': {
                'metavar': 'muted',
                'type': lambda arg: arg.lower() not in ('0', 'false', 'f', 'no', 'n')}},
        'swInfo': {'defaults': {'control': SystemControl, 'func': 'info'}},
        'notification': {
            'defaults': {'control': SystemControl, 'func': 'notify'},
            'arg': {'metavar': 'message'}},
        'off': {'defaults': {'control': SystemControl, 'func': 'power_off'}}
    }

    for parser_name, parser_setup in parsers.items():
        subparser = subparsers.add_parser(parser_name)
        subparser.set_defaults(**parser_setup['defaults'])
        if 'arg' in parser_setup:
            subparser.add_argument('arg', **parser_setup['arg'])
        if 'args' in parser_setup:
            for arg in parser_setup['args']:
                subparser.add_argument(*arg.pop('flags'), **arg)

    return parser.parse_args(args) if args else parser.parse_args()


def client_connect(host):
    client = WebOSClient(host)
    client.connect()
    return client


def client_register(client, store):
    for status in client.register(store):
        if status == WebOSClient.PROMPTED:
            print("Please accept the connect on the TV!")
        elif status == WebOSClient.REGISTERED:
            logging.info("Registration successful!")
    return store


if __name__ == '__main__':
    args = parse_args()

    if args.func == 'discover' and args.control == WebOSClient:
        for discovery in WebOSClient.discover():
            print(discovery.host)

    elif args.func == 'connect' and args.control == WebOSClient:
        client = client_connect(args.arg)
        store = client_register(client, {'ip': args.arg})
        save_config(args.output_config, store)

    else:
        store = get_config(args.config)
        client = client_connect(store['ip'])
        client_register(client, store)
        control = args.control(client)
        command = control.exec_command(args.func, control.COMMANDS[args.func])
        print(command(args.arg) if 'arg' in args else command())
