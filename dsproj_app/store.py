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

    def copy(self, store):
        self.store = store

    def length(self):
        return len(self.store)

    def reset(self):
        self.store = {}
