class Timestamp:

    def __init__(self):
        self.latest_timestamp = 0

    def get_timestamp(self):
        return self.latest_timestamp

    def set_timestamp(self, timestamp):
        self.latest_timestamp = timestamp

    def max_timestamp(self, other_timestamp):
        max_latest_timestamp = max(self.latest_timestamp, other_timestamp)
        return max_latest_timestamp
