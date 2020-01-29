import json
import numpy


class MyJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, numpy.integer):
            return int(o)
        elif isinstance(o, numpy.floating):
            return float(o)
        elif isinstance(o, numpy.ndarray):
            return o.tolist()
        else:
            return super(MyJsonEncoder, self).default(o)


def to_json_string(o):
    return json.dumps(o, ensure_ascii=False, cls=MyJsonEncoder)