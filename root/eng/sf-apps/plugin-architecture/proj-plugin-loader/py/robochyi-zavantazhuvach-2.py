class PluginError(Exception):
    """Плагін не придатний — з поясненням, придатним для журналу."""


def load_one(pyfile: Path) -> object:
    """Оживити ОДИН файл у модуль і звірити версію контракту.
    Кидає PluginError із людською причиною, якщо щось не так."""
    name = f"plugins.{pyfile.stem}"

    # -- фаза «завантажити»: тут виконується ЧУЖИЙ код верхнього рівня --
    spec = importlib.util.spec_from_file_location(name, pyfile)
    if spec is None or spec.loader is None:
        raise PluginError(f"{pyfile.name}: не вдалося прочитати як модуль")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module          # щоб модуль знаходив себе за іменем
    try:
        spec.loader.exec_module(module)  # <-- гострий крок: виконати файл
    except Exception as e:
        sys.modules.pop(name, None)      # прибрати напівживий модуль
        # ланцюжок винятку зберігаємо через "from e" — у журналі буде видно,
        # ЩО саме кинув плагін і на якому рядку його файлу
        raise PluginError(f"{pyfile.name}: збій при завантаженні: {e!r}") from e

    # -- фаза «звірити версію»: раніше, ніж чіпати register --
    api = getattr(module, "PLUGIN_API", None)
    if api != HOST_API:
        raise PluginError(
            f"{pyfile.name}: несумісний контракт "
            f"(плагін під API {api!r}, ядро дає {HOST_API})"
        )
    if not hasattr(module, "register"):
        raise PluginError(f"{pyfile.name}: немає точки входу register(host)")
    return module
