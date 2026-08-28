class ShapeRegistry:
    def __init__(self):
        self._prototypes = {}

    def register(self, key, proto):        # покласти зразок під ключем
        self._prototypes[key] = proto
    def create(self, key):
        return self._prototypes[key].clone()   # новий об'єкт — копія зразка

registry = ShapeRegistry()
registry.register("коло", Circle(0, 0, 10))    # зразок налаштовано раз
c = registry.create("коло")                    # далі — лише копії
