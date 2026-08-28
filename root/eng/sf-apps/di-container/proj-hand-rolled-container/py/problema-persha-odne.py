def resolve(self, promise):
    # 0. чи вже є готовий? одинак — віддати збережене, не будувати вдруге
    if promise in self._cache:
        return self._cache[promise]

    impl = self._bindings.get(promise, promise)
    sig = inspect.signature(impl.__init__)
    params = [p for name, p in sig.parameters.items() if name != "self"]
    args = [self.resolve(p.annotation) for p in params]

    obj = impl(*args)
    self._cache[promise] = obj      # запам'ятати — наступний раз повернемо цей самий
    return obj
