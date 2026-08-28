def make_lazy_spec_loader(module_name: str) -> types.ModuleType:
    """
    Створення відкладеного модуля на основі штатного importlib.util.LazyLoader.
    """
    spec = importlib.util.find_spec(module_name)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot find module spec for '{module_name}'")

    # Обгортаємо штатний завантажувач у LazyLoader
    loader = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader

    # Створюємо екземпляр модуля та реєструємо його в sys.modules
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    
    # Виклик exec_module не завантажує код негайно, а встановлює хук
    loader.exec_module(module)
    return module
