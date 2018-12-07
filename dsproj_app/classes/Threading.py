# from dsproj_app.views import get_array_views
from dsproj_app.classes.Store import Store
from dsproj_app.classes.VectorClock import VectorClock
from dsproj_app.views import get_array_views
from urllib.parse import parse_qs
from os import environ
from sys import exc_info
from time import sleep
import requests
import random
import threading
import json


class Threading(object):
    def __init__(self, details, interval=5):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval
        self.store = details["store"]
        self.clock = details["clock"]
        self.latest_timestamp = details["latest_timestamp"]
        self.causal_context = details["causal_context"]
        self.shards = details["shards"]
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True

        thread.start()  # Start the execution

    # def toggle(self, toggle):
    #     self.should_run = toggle

    def gossip(self):

        store = self.store
        clock = self.clock
        latest_timestamp = self.latest_timestamp
        causal_context = self.causal_context

        view_arr = environ.get("VIEW").split(",")
        # print(view_arr)
        # print("========================")
        if environ.get("IP_PORT") in view_arr and len(view_arr) != 1:
            # print(environ.get("VIEW"))
            # print("AHHHH", self.shards.get_directory())
            # print(environ.get("IP_PORT"))
            target_shard = self.shards.find_shardID_given_address(
                environ.get("IP_PORT")
            )
            shards_directory = self.shards.get_directory()
            ip_port_options = []

            if target_shard == None or target_shard not in shards_directory:
                return

            for ipport in shards_directory[target_shard]:
                ip_port_options.append(ipport)

            if environ.get("IP_PORT") in ip_port_options:
                ip_port_options.remove(environ.get("IP_PORT"))

            if len(ip_port_options) < 1:
                return
                
            random_IP_PORT = random.choice(ip_port_options)

            url = "http://" + random_IP_PORT + "/node-info"

            try:

                gresponse = requests.get(url, data={})
                data = gresponse.json()  # node to be gossiped (incoming node)
                is_current_clock_greater = clock.greater_than_or_equal(
                    data["clock"]
                )  # fucks up at this line

                # print("LOCAL clock = ", clock.get_vc())
                # print("OTHER clock = ", data["clock"])

                if len(clock.get_vc()) != len(data["clock"]):
                    return "0"

                if is_current_clock_greater == "equal":
                    # print("clocks are equal... do nothing")
                    pass
                elif is_current_clock_greater == True:
                    # print("current_clock_greater is true")
                    text = "vector"
                    new_item = self.merge_and_clobber_loser(data["store"], store.get())
                    # store.copy(new_item)    # this line doesn't make sense
                    data["store"] = new_item
                    self.update_gossip_node(
                        store, clock, latest_timestamp, random_IP_PORT, text
                    )

                elif is_current_clock_greater == False:
                    text = "vector"
                    new_item = self.merge_and_clobber_loser(store.get(), data["store"])
                    data["store"] = new_item
                    self.update_local_node(data, clock, latest_timestamp, text, store)

                else:
                    text = "timestamp"
                    localvc = clock.get_vc()
                    for i, val in enumerate(data["clock"]):
                        highest_val = max(localvc[i], val)
                        clock.update_vc(i, highest_val)
                        data["clock"][i] = highest_val

                    if latest_timestamp.get_timestamp() > float(
                        data["latest_timestamp"]
                    ):
                        new_item = self.merge_and_clobber_loser(
                            data["store"], store.get()
                        )
                        store.copy(new_item)
                        self.update_gossip_node(
                            store, clock, latest_timestamp, random_IP_PORT, text
                        )
                    else:
                        new_item = self.merge_and_clobber_loser(
                            store.get(), data["store"]
                        )
                        data["store"] = new_item
                        self.update_local_node(
                            data, clock, latest_timestamp, text, store
                        )

            except Exception as e:
                print("================error in gossip================")
                print("Error:", e)

    def run(self):
        """ Method that runs forever """
        while True:
            # Do something
            self.gossip()
            sleep(self.interval)

    def merge_and_clobber_loser(self, loser, winner):
        new_item = {}

        # get any item from loser not in winner
        for key in loser:
            if key not in winner:
                new_item[key] = loser[key]

        # merge
        new_item.update(winner)

        # update store\
        return new_item

    def update_gossip_node(self, store, clock, latest_timestamp, random_IP_PORT, text):
        payload = {
            "payload": {
                "store": store.get(),
                "clock": clock.get_vc(),
                "latest_timestamp": latest_timestamp.get_timestamp(),
            }
        }
        url = "http://" + random_IP_PORT + "/update-node"
        payload = "payload=" + json.dumps(payload)
        requests.put(url, data=payload)
        # print("gossiped node updated via ", text)

    def update_local_node(self, data, clock, latest_timestamp, text, store):
        clock.copy_vc(data["clock"])
        latest_timestamp.set_timestamp(data["latest_timestamp"])

        # store.copy returns an object
        # print(self.store.copy())
        # data['store'] = self.store.get()
        self.store.overwrite_store(data["store"])
        # print("local node updated via ", text)
