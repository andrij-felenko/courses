function lint(d: Decision, history: Window[]): string[] {
  const warn: string[] = [];
  if (!d.uncertainty.trim())
    warn.push("невизначеність не названо — це прокрастинація, не відкладання");
  if (d.options.length < 2)
    warn.push("менше двох живих опцій — вибір уже зроблено за замовчуванням");
  if (d.trigger.conditions.length === 0)
    warn.push("тригер без умов — спрацює будь-коли");
  if (d.trigger.leadWeeks <= 0)
    warn.push("leadWeeks ≤ 0: стріляємо на пробитому порозі — спізнимось на час втілення");
  for (const c of d.trigger.conditions) {
    const noBand = c.dir === "rising" ? c.fireAt < c.armAt : c.fireAt > c.armAt;
    if (noBand) warn.push(`${c.signal}: fire по той бік arm — смуги гістерезису немає`);
  }
  // «Тригер, що не спрацює ніколи»: чи хоч раз спрацював би на реальній історії?
  if (history.length > 0 && !history.some(w => isFiring(d.trigger, w)))
    warn.push("на всій історії тригер не спрацював би жодного разу — поріг недосяжний?");
  return warn;
}
