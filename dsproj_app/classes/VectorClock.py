from ast import literal_eval


class VectorClock:

    def __init__(self, size, index):
        self.vc = [0]*size
        self.index = index
        self.size = size

    def get_vc(self):
        return self.vc

    def get_size(self):
        return self.size

    def get_index(self):
        return self.index

    def update_vc(self, index, new_val):
        self.vc[index] = new_val

    def copy_vc(self, other_vc):
        self.vc = other_vc

    def increment_index(self, index):
        self.vc[index] += 1

    def increment_self(self):
        print("self.index:", self.index)
        self.vc[self.index] += 1

    def push(self):
        self.vc.append(0)

    def remove_vc(self, index):
        if index < self.index:
            self.index-=1
        self.vc.pop(index)

    # True: self.vc is less than other_vc
    # False: self.vc is greater than other_vc
    # None is concurrent.
    def greater_than_or_equal(self, other_vc):
        # print("self {}".format(self.vc))
        # print("other {}".format(other_vc))
        # if vectors are the same, incomparable
        if self.vc == other_vc:
            return "equal"

        # records 2 instances where vectors
        # alternate overpowering each other's components
        bad1 = False
        bad2 = False
        for i in range(0, self.size-1):
            if self.vc[i] < other_vc[i]:
                bad1 = True
            if self.vc[i] > other_vc[i]:
                bad2 = True

        # if 2 instances recorded, incomparable
        if (bad1 and bad2):
            return None
        # if self has been smaller throughout entire iteration,
        # then, self.vc is not bigger
        elif bad1 == True:
            return False
        # if self has been bigger througout entire iteration,
        # then, self.vs is bigger
        elif bad2 == True:
            return True

    def reset(self):
        for idx, val in enumerate(self.vc):
            self.vc[idx] = 0
