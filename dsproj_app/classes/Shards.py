from dsproj_app.views import get_array_views
from os import environ


class Shards:
    def __init__(self, number):
        self.shard_size = int(number)
        self.past_shard_size = int(number)
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
        # print("In get_members_in_ID: ", self.shard_directory)
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
        return self.find_shardID_given_address(environ.get("IP_PORT"))

    def get_shard_size(self):
        return self.shard_size

    def change_shard_size_superficial(self, count):
        self.shard_size = count

    def delete_shard_directory_key(self, key):
        del self.shard_directory[str(key)]

    def build_directory(self):
        for idx, IP_PORT in enumerate(self.views):
            self.shard_directory[str(idx % self.shard_size)] = []

        if self.num_nodes >= 2 * self.shard_size:
            for idx, IP_PORT in enumerate(self.views):
                self.shard_directory[str(idx % self.shard_size)].append(IP_PORT)
        elif self.shard_size >= self.num_nodes and self.num_nodes / 2 > 1:
            self.shard_size = self.num_nodes / 2
            for idx, IP_PORT in enumerate(self.views):
                self.shard_directory[str(idx % self.shard_size)].append(IP_PORT)
        else:
            self.shard_size = 1
            self.shard_directory["0"] = self.views

    def update(self, num_shards, store):
        if self.past_shard_size != num_shards:
            print("past: ", self.past_shard_size)
            print("now: ", num_shards)
            num_shards = int(num_shards)
            response = {"is_successful": False, "msg": None, "result": "Error"}
            if num_shards == 0:
                response["msg"] = "Must have at least one shard"
            elif self.num_nodes >= 2 * num_shards:
                # redistribute all data and rehash on the new shard
                # call your rehash function here. should refer to store maybe? pass in shards instance if needed

                self.shard_size = num_shards
                self.reset_shard()
                # rehashes the shard directory with new shard #
                self.build_directory()
                store.rehash_keys(self.shard_directory, self.shard_size)
                response = {
                    "is_successful": True,
                    "result": "Success",
                    "shard_ids": self.get_keys(),
                }
            elif num_shards >= self.num_nodes:
                response["msg"] = "Not enough nodes for " + str(num_shards) + " shards"
            else:
                response["msg"] = (
                    "Not enough nodes. "
                    + str(num_shards)
                    + " shards result in a nonfault tolerant shard"
                )
            self.past_shard_size = self.shard_size
            return response
        return None

    def update_view(self):
        self.views = get_array_views()
        self.num_nodes = len(self.views)

    def remove_node(self, index, node_to_delete):
        if (
            str(index) in self.shard_directory
            and node_to_delete in self.shard_directory[str(index)]
        ):
            self.shard_directory[str(index)].remove(node_to_delete)
            return True
        else:
            return None

    def add_node(self, index, node_to_add):
        if (
            str(index) in self.shard_directory
        ):
            self.shard_directory[str(index)].append(node_to_add)
            return True
        else:
            return None

    def reset_shard(self):
        self.shard_directory = {}
        for idx, IP_PORT in enumerate(self.views):
            self.shard_directory[str(idx % self.shard_size)] = []

    def find_shardID_given_address(self, given_address):
        for key in self.get_directory():
            # print("SHARDID", key)
            # print("DIRECTORY", self.get_directory()[key])
            for address in self.get_directory()[key]:
                if given_address == address:
                    return key
