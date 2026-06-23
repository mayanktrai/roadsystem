import yaml
import os

class Config:
    def __init__(self, data):
        self.data = data

    @classmethod
    def load(cls, path):
        if not os.path.exists(path):
            return cls({})
        with open(path, 'r') as f:
            return cls(yaml.safe_load(f) or {})

    def get(self, key, default=None):
        keys = key.split('.')
        val = self.data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val