import argparse
import json
import logging
import os

from pywebostv.connection import WebOSClient
from pywebostv.controls import (
    MediaControl, SystemControl, ApplicationControl, InputControl, SourceControl)


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

    parser_scan = subparsers.add_parser('scan')
    parser_scan.set_defaults(control=WebOSClient, func='discover')

    parser_audio_volume = subparsers.add_parser('audioVolume')
    parser_audio_volume.set_defaults(control=MediaControl, func='get_volume')
    parser_volume_up = subparsers.add_parser('volumeUp')
    parser_volume_up.set_defaults(control=MediaControl, func='volume_up')
    parser_volume_down = subparsers.add_parser('volumeDown')
    parser_volume_down.set_defaults(control=MediaControl, func='volume_down')
    parser_set_volume = subparsers.add_parser('setVolume')
    parser_set_volume.add_argument('arg', metavar='level', type=int)
    parser_set_volume.set_defaults(control=MediaControl, func='set_volume')
    parser_mute = subparsers.add_parser('mute')
    parser_mute.add_argument('arg', metavar='muted', type=(
        lambda arg: arg.lower() not in ('0', 'false', 'f', 'no', 'n')))
    parser_mute.set_defaults(control=MediaControl, func='mute')

    parser_mute = subparsers.add_parser('swInfo')
    parser_mute.set_defaults(control=SystemControl, func='info')
    parser_mute = subparsers.add_parser('notification')
    parser_mute.add_argument('arg', metavar='message')
    parser_mute.set_defaults(control=SystemControl, func='notify')
    parser_mute = subparsers.add_parser('off')
    parser_mute.set_defaults(control=SystemControl, func='power_off')

    return parser.parse_args(args) if args else parser.parse_args()


def get_config(config_file):
    store = {}
    if os.path.exists(config_file):
        with open(config_file) as fp:
            settings = json.load(fp)
        store['client_key'] = settings["client-key"]
        store['ip'] = settings['ip']
    return store


def client_connect(store):
    client = WebOSClient(store['ip'])
    client.connect()
    for status in client.register(store):
        if status == WebOSClient.PROMPTED:
            print("Please accept the connect on the TV!")
        elif status == WebOSClient.REGISTERED:
            logging.info("Registration successful!")
    return client


if __name__ == '__main__':
    args = parse_args()

    store = get_config(args.config)

    if args.func == 'discover' and args.control == WebOSClient:
        for discovery in WebOSClient.discover():
            print(discovery.host)

    else:
        client = client_connect(store)
        control = args.control(client)
        command = control.exec_command(args.func, control.COMMANDS[args.func])
        print(command(args.arg) if 'arg' in args else command())
