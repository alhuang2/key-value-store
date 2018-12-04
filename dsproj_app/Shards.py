from dsproj_app.views import get_array_views
from os import environ


class Shards:
    def __init__(self, number):
        self.shard_size = int(number)
        self.views = get_array_views()
        self.num_nodes = len(self.views)
        self.shard_directory = {}

        for idx, IP_PORT in enumerate(self.views):
            self.shard_directory[idx % self.shard_size] = []

        if self.num_nodes >= 2 * self.shard_size:
            for idx, IP_PORT in enumerate(self.views):
                self.shard_directory[idx % self.shard_size].append(IP_PORT)
        elif self.shard_size >= self.num_nodes and self.num_nodes/2 > 1:
            self.shard_size = self.num_nodes/2
            for idx, IP_PORT in enumerate(self.views):
                self.shard_directory[idx % self.shard_size].append(IP_PORT)
        else:
            # # of nodes = 3 or something liek that.
            self.shard_size = 1
            self.shard_directory[0] = self.views

        self.my_shard = self.views.index(
            environ.get("IP_PORT")) % self.shard_size

    def get_directory(self):
        return self.shard_directory

    def get_my_members(self):
        members = self.shard_directory[self.my_shard]
        result_arr = []
        for member in members:
            result_arr.append(member)
        return result_arr

    def get_members_in_ID(self, id):
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

    def update_shard_size(self, new_size):
        self.shard_size = new_size
        # maybe call function to reevaluate and redistrbute data here?
        return True
