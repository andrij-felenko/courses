type Reading = { at: number; celsius: number };   // at — epoch, мс
type Policy  = { threshold: number; windowMs: number };

// Чисте рішення: ні годинника, ні бази — самі значення на вході.
function decideCooling(readings: Reading[], now: number, policy: Policy): "on" | "off" {
  const inWindow = readings.filter(r => r.at >= now - policy.windowMs);
  if (inWindow.length === 0) return "off";                 // немає свідчень — не вмикаємо
  const avg = inWindow.reduce((s, r) => s + r.celsius, 0) / inWindow.length;
  return avg > policy.threshold ? "on" : "off";
}
