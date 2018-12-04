from dsproj_app.views import get_array_views
from os import environ


class Shards:
    def __init__(self, number):
        self.shard_size = int(number)
        self.views = get_array_views()
        self.num_nodes = len(self.views)
        self.shard_directory = {}

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
            # # of nodes = 3 or something liek that.
            self.shard_size = 1
            self.shard_directory["0"] = self.views

        self.my_shard = str(self.views.index(
            environ.get("IP_PORT")) % self.shard_size)

    # return shard_id: associated_IPs
    def get_directory(self):
        return self.shard_directory

    # return all th IP's associated with current container's shard
    def get_my_members(self):
        members = self.shard_directory[self.my_shard]
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

    # updates to new number of shards if possible
    # returns {
    #   "is_successful": True or False,
    #   "result": Success, Error
    #   "shard_ids": "0,1,2", IF TRUE
    #   "msg": "Not enough nodes for <num_shards> shards", IF FALSE
    #   “msg”: “Not enough nodes. <number> shards result in a nonfault tolerant shard”}, IF FALSE
    # }
    # Status = 200 or 400
    def update(self, num_shards):
        if self.num_nodes >= 2 * int(num_shards):
            # redistribute all data and rehash on the new shard
            pass    
        return True

    def update_view(self):
        self.views = get_array_views()
        self.num_nodes = len(self.views)
