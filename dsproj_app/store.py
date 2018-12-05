import requests
import random
from hashlib import sha1
from os import environ

class Store:

    # tomstone = True means deleted

    def __init__(self):
        self.store = {}

    def has_key(self, key):
        return key in self.store

    def get(self):
        return self.store

    def is_exists(self, key):
        if key in self.store:
            stuff = self.store[key]
            return stuff["tombstone"] == False
        return False

    def get_item(self, key):
        if key in self.store:
            return self.store[key]
        else:
            return None

    def add(self, key, value, causal_context):
        self.store[key] = {
            "val": value,
            "causal_context": causal_context,
            "tombstone": False
        }
        return True

    def delete_key(self, key):
        if key in self.store:
            stuff = self.store[key]
            stuff["tombstone"] = True
            return True
        else:
            return False
    
    def rehash_keys(self, directory, num_shards):
        copy_store = self.copy()
        self.store = {}
        data = {"toggle": False, "is_broadcaster": True}
        requests.put("http://"+environ.get("IP_PORT")+"/toggle_gossip", data=data)
        for key, obj in copy_store.items():
            binary_key = sha1(key.encode())
            shard_location = int(binary_key.hexdigest(),16) % num_shards
            members = directory[str(shard_location)]
            rand_address = random.choice(members)

            data = "val="+obj['val']+"&&payload={}"
            requests.put(
                "http://"+rand_address+"/keyValue-store/"+key, data=data
            )
        data = {"toggle": True, "is_broadcaster": True}
        requests.put("http://"+environ.get("IP_PORT")+"/toggle_gossip", data=data)
                        

    def copy(self):
        new_store = {}
        for key, obj in self.store.items():
            new_store[key] = obj
        return new_store

    def length(self):
        return len(self.store)

    def reset(self):
        self.store = {}
