from dsproj_app.views import get_array_views
from os import environ


class Shards:
    def __init__(self, number):
        self.shard_size = int(number)
        self.views = get_array_views()
        self.num_nodes = len(self.views)
        self.shard_directory = {}
        self.build_directory()

    # return shard_id: associated_IPs
    def get_directory(self):
        return self.shard_directory

    # return all th IP's associated with current container's shard
    def get_my_members(self, my_shard_idx):
        members = self.shard_directory[my_shard_idx]
        result_arr = []
        for member in members:
            result_arr.append(member)
        return result_arr

    # gets all the IP's associated with that shard ID
    def get_members_in_ID(self, id):
        id = str(id)
        if id in self.shard_directory:
            return self.shard_directory[id]
        else:
            return None

    def get_keys(self):
        keys = []
        for key in self.shard_directory:
            keys.append(key)
        return ",".join(keys)

    def get_my_shard(self):
        return self.my_shard

    def get_shard_size(self):
        return self.shard_size

    def build_directory(self):
        

        for idx, IP_PORT in enumerate(self.views):
            self.shard_directory[str(idx % self.shard_size)] = []

        if self.num_nodes >= 2 * self.shard_size:
            for idx, IP_PORT in enumerate(self.views):
                self.shard_directory[str(
                    idx % self.shard_size)].append(IP_PORT)
        elif self.shard_size >= self.num_nodes and self.num_nodes/2 > 1:
            self.shard_size = self.num_nodes/2
            for idx, IP_PORT in enumerate(self.views):
                self.shard_directory[str(
                    idx % self.shard_size)].append(IP_PORT)
        else:
            self.shard_size = 1
            self.shard_directory["0"] = self.views

        if environ.get("IP_PORT") in self.views:   
            self.my_shard = str(self.views.index(
                environ.get("IP_PORT")) % self.shard_size)
        else:
            self.my_shard = None

    # updates to new number of shards if possible
    # returns {
    #   "is_successful": True or False,
    #   "result": Success, Error
    #   "shard_ids": "0,1,2", IF TRUE
    #   "msg": "Not enough nodes for <num_shards> shards", IF FALSE
    #   “msg”: “Not enough nodes. <number> shards result in a nonfault tolerant shard”}, IF FALSE
    # }
    # Status = 200 or 400
    def update(self, num_shards, store):
        num_shards = int(num_shards)
        response = {
            "is_successful": False,
            "msg": None,
            "result": "Error"
        }
        if self.num_nodes >= 2 * num_shards:
            # redistribute all data and rehash on the new shard
            # call your rehash function here. should refer to store maybe? pass in shards instance if needed
            self.shard_size = num_shards
            self.reset_shard()
            # rehashes the shard directory with new shard #
            self.build_directory()
            store.rehash_keys(self.shard_directory, self.shard_size)
        elif num_shards == 1:
            # combine all shard data and put it on all nodes
            # maybe the same thing as the one above ? ^^
            pass
        elif num_shards == 0:
            response['msg'] = "Must have at least one shard"
        elif num_shards >= self.num_nodes:
            response['msg'] = "Not enough nodes for "+num_shards+" shards"
        else:
            response['msg'] = "Not enough nodes. "+num_shards + \
                " shards result in a nonfault tolerant shard"
        return response

    def update_view(self):
        self.views = get_array_views()
        self.num_nodes = len(self.views)

    def remove_node(self, index, node_to_delete):
        self.shard_directory[str(index)].remove(node_to_delete)

    def add_node(self, index, node_to_add):
        self.shard_directory[str(index)].append(node_to_add)
    
    def reset_shard(self):
        self.shard_directory = {}
        for idx, IP_PORT in enumerate(self.views):
            self.shard_directory[str(idx % self.shard_size)] = []

    def find_shardID_given_address(self, given_address):
        for key in self.get_directory():
            print("GODSHITTTT", key)
            print("GODSHIT", self.get_directory()[key])
            for address in self.get_directory()[key]:
                if given_address == address:
                    return key
                
