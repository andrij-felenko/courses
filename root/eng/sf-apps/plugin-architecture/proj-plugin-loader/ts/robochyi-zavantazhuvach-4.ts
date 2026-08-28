async function main(): Promise<void> {
  const registry = new ExportRegistry();
  await loadPlugins(path.resolve("plugins"), registry);  // могли бути й гнилі файли

  // ядро працює з тими, що завантажились; несправні просто відсутні в реєстрі
  const doc = /* якийсь документ ядра */ null as unknown as Document;
  try {
    const data = registry.exportAs("md", doc);
  } catch { /* плагіна .md не завантажилось — ядро це переживає */ }
}
main();
