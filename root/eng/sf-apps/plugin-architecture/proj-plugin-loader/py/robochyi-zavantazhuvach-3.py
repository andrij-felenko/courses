def load_plugins(folder: Path, registry: ExportRegistry) -> None:
    host = Host(registry)
    loaded, failed = 0, 0

    for pyfile in sorted(folder.glob("*.py")):
        if pyfile.name.startswith("_"):
            continue                      # службові файли — не плагіни
        try:
            module = load_one(pyfile)     # фази 1-2: завантажити + звірити версію

            # -- фаза «register»: знову ЧУЖИЙ код, знову під пасткою --
            try:
                module.register(host)     # <-- плагін вписує себе в реєстр
            except Exception as e:
                raise PluginError(
                    f"{pyfile.name}: register(host) кинув {e!r}"
                ) from e

        except PluginError as e:
            # ЄДИНЕ місце, де збій плагіна гаситься: логуємо й беремо наступний.
            log.warning("плагін пропущено — %s", e)
            failed += 1
            continue                      # <-- ядро НЕ падає, цикл іде далі
        else:
            loaded += 1

    log.info("плагінів завантажено: %d, пропущено: %d", loaded, failed)
