class SortInfo():
    
    def __init__(self, pKey, value):
        self.pKey = pKey
        self.value = value
    
    def __eq__(self, other):
        return self.pKey == other.pKey and self.value == other.value
    
    def __lt__(self, other):
        return self.value < other.value