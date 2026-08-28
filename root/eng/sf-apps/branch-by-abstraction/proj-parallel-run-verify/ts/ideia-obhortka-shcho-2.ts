// На час спостереження клієнт отримує звіряч замість готової реалізації
function makeRenderer(flags: Flags): Renderer {
  const legacy = new LegacyRenderer();
  const modern = new ModernRenderer();

  if (flags.enabled("render-shadow-compare")) {
    return new ComparingRenderer(legacy, modern, mismatchLog);
  }
  return flags.enabled("render-use-modern") ? modern : legacy;
}
