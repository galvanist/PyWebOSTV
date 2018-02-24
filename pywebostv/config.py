import json
import os


def get_config(config_file):
    store = {}
    if os.path.exists(config_file):
        with open(config_file) as fp:
            settings = json.load(fp)
        store['client_key'] = settings["client-key"]
        store['ip'] = settings['ip']
    return store

def save_config(config_file, store):
    store['client-key'] = store.pop('client_key')
    json.dump(store, config_file)
    return store
