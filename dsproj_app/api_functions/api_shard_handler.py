from dsproj_app.Shards import Shards


#return JSON pls
def shard_handler(request, method, shards):
    pass

# PUT /shard/changeShardNumber -d=”num=<number>”
# Should initiate a change in the replica groups such that the key-values are redivided
#  across <number> groups and returns a list of all shard ids, as in GET /shard/all_ids
# {“result”: “Success”,
# “shard_ids”: “0,1,2”},
# Status = 200
# If <number> is greater than the number of nodes in the view, please return:
# {“result”: “Error”,
# “msg”: “Not enough nodes for <number> shards”},
# Status = 400
# If there is only 1 node in any partition as a result of redividing into <number> shards, 
# abort the operation and return:
# {“result”: Error”,
# “msg”: “Not enough nodes. <number> shards result in a nonfault tolerant shard”},
# Status = 400
# The only time one should have 1 node in a shard is if there is only one node in the entire system. 
# In this case it should only return an error message if you try to increase the number of shards beyond 1, 
# you should not return the second error message in this case.
def put():
    pass

# returns all id's
# GET /shard/my_id
# Should return the container’s shard id
# {“id”:<container’sShardId>},
# Status = 200
def get_id():
    pass

# return specific id
# GET /shard/all_ids
# Should return a list of all shard ids in the system as a string of comma separated values.
# {“result”: “Success”,
# “shard_ids”: “0,1,2”},
# Status = 200
def get():
    pass

# returns all the IP_PORTS associated with that shard ID
# GET /shard/members/<shard_id>
# Should return a list of all members in the shard with id <shard_id>. 
# Each member should be represented as an ip-port address. (Again, the same one you pass into VIEW)
# {“result” : “Success”,
# “members”: “176.32.164.2:8080,176.32.164.3:8080”},
# Status = 200
# If the <shard_id> is invalid, please return:
# {“result”: “Error”,
# “msg”: “No shard with id <shard_id>”},
# Status = 404
def get_members_in_ID():
    pass

# GET /shard/count/<shard_id>
# Should return the number of key-value pairs that shard is responsible for as an integer
# {“result”: “Success”,
# “Count”: <numberOfKeys> },
# Status = 200
# If the <shard_id> is invalid, please return:
# {“result”: “Error”,
# “msg”: “No shard with id <shard_id>”},
# Status = 404
def get_key_count_of_ID():
    pass

