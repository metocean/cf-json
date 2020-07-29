from json.encoder import JSONEncoder

INFINITY = float("inf")
FLOAT_REPR = float.__repr__


class CFEncoder(JSONEncoder):
    def __init__(self, **kwargs):
        JSONEncoder.__init__(self, **kwargs)
