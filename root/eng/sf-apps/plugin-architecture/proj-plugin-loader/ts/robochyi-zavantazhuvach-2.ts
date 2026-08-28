class PluginError extends Error {}   // плагін не придатний, із поясненням

interface PluginModule {
  PLUGIN_API?: unknown;
  register?: (host: Host) => void;
}

async function loadOne(file: string): Promise<PluginModule> {
  // -- фаза «завантажити»: тут виконується ЧУЖИЙ код верхнього рівня --
  let mod: PluginModule;
  try {
    // pathToFileURL обов'язковий: на Windows "C:\..." не є валідним
    // специфікатором модуля, а file://-URL — є.
    mod = (await import(pathToFileURL(file).href)) as PluginModule;
  } catch (e) {
    throw new PluginError(`${path.basename(file)}: збій при завантаженні: ${String(e)}`);
  }

  // -- фаза «звірити версію»: раніше, ніж чіпати register --
  if (mod.PLUGIN_API !== HOST_API) {
    throw new PluginError(
      `${path.basename(file)}: несумісний контракт ` +
      `(плагін під API ${String(mod.PLUGIN_API)}, ядро дає ${HOST_API})`,
    );
  }
  if (typeof mod.register !== "function") {
    throw new PluginError(`${path.basename(file)}: немає точки входу register(host)`);
  }
  return mod;
}
