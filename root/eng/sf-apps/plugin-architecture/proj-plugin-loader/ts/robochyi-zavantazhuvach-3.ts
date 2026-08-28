async function loadPlugins(folder: string, registry: ExportRegistry): Promise<void> {
  const host = new HostImpl(registry);
  let loaded = 0, failed = 0;

  const entries = (await readdir(folder))
    .filter(n => n.endsWith(".js") && !n.startsWith("_"))
    .sort();

  for (const name of entries) {
    const file = path.join(folder, name);
    try {
      const mod = await loadOne(file);           // фази 1-2

      // -- фаза «register»: знову ЧУЖИЙ код, знову під пасткою --
      try {
        mod.register!(host);                      // плагін вписує себе в реєстр
      } catch (e) {
        throw new PluginError(`${name}: register(host) кинув ${String(e)}`);
      }
      loaded++;
    } catch (e) {
      if (e instanceof PluginError) {
        // ЄДИНЕ місце, де збій плагіна гаситься: логуємо й беремо наступний.
        log.warn(`плагін пропущено — ${e.message}`);
        failed++;
        continue;                                 // ядро НЕ падає
      }
      throw e;                                     // не наша помилка — не ковтаємо
    }
  }

  log.info(`плагінів завантажено: ${loaded}, пропущено: ${failed}`);
}
