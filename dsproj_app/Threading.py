# from dsproj_app.views import get_array_views
from dsproj_app.store import Store
from dsproj_app.VectorClock import VectorClock
from dsproj_app.views import get_array_views
from urllib.parse import parse_qs
from os import environ
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
        self.should_run_gossip = details['should_run_gossip']
        self.interval = interval
        self.store = details['store']
        self.clock = details['clock']
        self.latest_timestamp = details['latest_timestamp']
        self.causal_context = details['causal_context']
        self.shards = details['shards']
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True

        thread.start()                                  # Start the execution

    def stop(self):
        pass

    def gossip(self):

        store = self.store
        clock = self.clock
        latest_timestamp = self.latest_timestamp
        causal_context = self.causal_context

        # members = self.shards.get_members_in_ID(self.shards.get_my_shard())
        # print("==========MEMBERS:==========", members)
        # # random_IP_PORT = random.choice(members)
        # if members != None:
        #     members.remove(environ.get("IP_PORT"))
        #     random_IP_PORT = random.choice(members)
        # else:
        #     return

        view_arr = environ.get("VIEW").split(",")
        # print(view_arr)
        # print("========================")
        if environ.get("IP_PORT") in view_arr and len(view_arr)!=1:
            # print(environ.get("VIEW"))
            # print("AHHHH", self.shards.get_directory())
            # print(environ.get("IP_PORT"))
            target_shard = self.shards.find_shardID_given_address(environ.get("IP_PORT"))
            shards_directory = self.shards.get_directory()
            # print(target_shard)
            ip_port_options = []
            for ipport in shards_directory[target_shard]:
                ip_port_options.append(ipport)
            ip_port_options.remove(environ.get("IP_PORT"))
            random_IP_PORT = random.choice(ip_port_options)

            url = "http://" + random_IP_PORT + "/node-info"
            print("get my members!!!!!!!!!!!!!!!!!!!!!")
            print("this is shard members", shards_directory[target_shard])
            print(self.shards.get_shard_size())
            try:
                gresponse = requests.get(url, data={})
                data = gresponse.json() # node to be gossiped (incoming node)
                print("#################3")
                print(data)
                print(self.store.get())
                print(self.clock.get_vc())
                print(self.latest_timestamp.get_timestamp())
                print("#####################")
                is_current_clock_greater = clock.greater_than_or_equal(
                    data['clock']) #fucks up at this line
                # print("a few lines after gossip")

                print("LOCAL clock = ", clock.get_vc())
                print("OTHER clock = ", data['clock'])

                if len(clock.get_vc()) != len(data['clock']):
                    return "0"
                print("THIS IS STORE-FIRST!!!!!!!!!!!", self.store.get())
                # print("========================")

                # print("data['store']=", data['store'])
                # print("type = ", type(data['store']))
                # print("store.get()=", store.get())
                # print("type = ", type(store.get()))

                if (is_current_clock_greater == "equal"):
                    print("clocks are equal... do nothing")
                    pass
                elif(is_current_clock_greater == True):
                    print("current_clock_greater is true")
                    text = "vector"
                    new_item = self.merge_and_clobber_loser(
                        data['store'], store.get())
                    # store.copy(new_item)    # this line doesn't make sense
                    data['store'] = new_item
                    self.update_gossip_node(
                        store, clock, latest_timestamp, random_IP_PORT, text)

                    print("THIS IS STORE!!!!!!!!!!!", self.store.get())
                elif(is_current_clock_greater == False):
                    print("current_clock_greater is false")
                    text = "vector"
                    new_item = self.merge_and_clobber_loser(
                        store.get(), data['store'])
                    print("THIS IS NEWITEM!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",new_item)
                    print("asshole")
                    print(data['store'])
                    data['store'] = new_item
                    print("THIS IS DATA[store]",data['store'])
                    self.update_local_node(
                        data, clock, latest_timestamp, text, store)
                    print("anus")
                    # print("THIS IS STORE!!!!!!!!!!!", self.store)

                else:
                    text = "timestamp"
                    localvc = clock.get_vc()
                    for i, val in enumerate(data['clock']):
                        highest_val = max(localvc[i], val)
                        clock.update_vc(i, highest_val)
                        data['clock'][i] = highest_val

                    if latest_timestamp.get_timestamp() > float(data['latest_timestamp']):
                        new_item = self.merge_and_clobber_loser(
                            data['store'], store.get())
                        store.copy(new_item)
                        self.update_gossip_node(
                            store, clock, latest_timestamp, random_IP_PORT, text
                        )
                    else:
                        new_item = self.merge_and_clobber_loser(
                            store.get(), data['store'])
                        data['store'] = new_item
                        self.update_local_node(
                            data, clock, latest_timestamp, text, store)
            except:
                print("================error in gossip================")



    def run(self):
        """ Method that runs forever """
        while self.should_run_gossip:
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
        print("newitem1: ", new_item)

        # delete any val with tombstone
        # for key in list(new_item):
        #     if new_item[key]["tombstone"] == True:
        #         del new_item[key]

        print("newitem2: ", new_item)
        # update store\
        return new_item

    def update_gossip_node(self, store, clock, latest_timestamp, random_IP_PORT, text):
        payload = {
            "payload": {
                "store": store.get(),
                "clock": clock.get_vc(),
                "latest_timestamp": latest_timestamp.get_timestamp()
            }
        }
        url = "http://" + random_IP_PORT + "/update-node"
        payload = "payload="+json.dumps(payload)
        requests.put(url, data=payload)
        print("gossiped node updated via ", text)

    def update_local_node(self, data, clock, latest_timestamp, text, store):
        clock.copy_vc(data['clock'])
        latest_timestamp.set_timestamp(data['latest_timestamp'])

        # store.copy returns an object
        print("FUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUCCCCCCKKKKKKKKK")
        # print(self.store.copy())
        # data['store'] = self.store.get()
        self.store.overwrite_store(data['store'])
        print("local node updated via ", text)
