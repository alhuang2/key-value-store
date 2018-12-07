import threading
from os import environ


class Rebalance(threading.Thread):
    """Thread that executes a task every N seconds"""

    def __init__(self, interval, shards, store):

        self._finished = threading.Event()
        self._interval = interval
        self.shards = shards
        self.store = store

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    # def setInterval(self, interval):
    #     """Set the number of seconds we sleep between executing our task"""
    #     self._interval = interval

    def shutdown(self):
        """Stop this thread"""
        self._finished.set()

    def run(self):
        while True:
            if self._finished.isSet():
                return
            self.task()

            # sleep for interval or until shutdown
            self._finished.wait(self._interval)

    def task(self):
        """The task done by this thread - override in subclasses"""
        print("Rebalance: ", environ.get("IP_PORT"))
        print("shard count: ", self.shards.get_shard_size())
        self.shards.update(self.shards.get_shard_size(), self.store)
