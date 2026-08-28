import inspect

class Container:
    def __init__(self):
        self._bindings = {}

    def bind(self, promise, impl):
        self._bindings[promise] = impl
        return self

    def resolve(self, promise):
        # 1. яку реалізацію будувати за цією обіцянкою
        impl = self._bindings.get(promise, promise)   # нема прив'язки — будуємо сам тип

        # 2. що просить конструктор impl — читаємо рефлексією
        sig = inspect.signature(impl.__init__)
        params = [p for name, p in sig.parameters.items() if name != "self"]

        # 3. для КОЖНОГО параметра — рекурсивно зібрати його за типом-анотацією
        args = [self.resolve(p.annotation) for p in params]

        # 4. усі залежності в руках — покликати конструктор
        return impl(*args)
