class PrototypeRegistry:
    def __init__(self):
        self._prototypes = {}

    def register(self, key, proto):          # покласти зразок під ключем
        self._prototypes[key] = proto

    def create(self, key):
        proto = self._prototypes.get(key)
        if proto is None:
            raise KeyError(f"немає прототипу: {key}")
        return proto.clone()                 # новий об'єкт — копія зразка
