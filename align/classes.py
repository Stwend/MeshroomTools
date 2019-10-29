class Bucket:
    location = None
    def __init__(self, name, side, item):
        self.name = name
        self.side = side
        self.items = [item]


class BucketItem:
    def __init__(self, value, weight = 1, side = 1):
        self.value = value
        self.weight = weight
        self.side = side