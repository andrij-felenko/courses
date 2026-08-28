const reg: Stakeholder[] = [
  { name: "Замовник",     power: true,  legitimacy: true,  urgency: false, interest: true,  concern: "вартість" },
  { name: "Спонсор",      power: true,  legitimacy: true,  urgency: false, interest: false, concern: "вартість" },
  { name: "Оператор",     power: false, legitimacy: true,  urgency: true,  interest: true,  concern: "доступність" },
  { name: "Аудитор",      power: true,  legitimacy: true,  urgency: true,  interest: true,  concern: "безпека", hard: true },
  { name: "Супровід",     power: false, legitimacy: true,  urgency: false, interest: true,  concern: "змінюваність" },
  { name: "Користувач",   power: false, legitimacy: true,  urgency: false, interest: true,  concern: "швидкодія" },
  { name: "Постачальник", power: false, legitimacy: true,  urgency: false, interest: false, concern: "вартість" },
];

const decisions: Decision[] = [
  { name: "бюджет і план-графік",    closes: "вартість" },
  { name: "плагіни способів оплати", closes: "змінюваність" },
  { name: "кеш гарячих запитів",     closes: "швидкодія" },
];

const params: Parameter[] = [
  { name: "ширина реплікації даних", pushes: [{ attr: "доступність", dir: 1 }, { attr: "безпека", dir: -1 }] },
  { name: "розмір пулу потоків",     pushes: [{ attr: "швидкодія", dir: 1 }] },                                  // точка чутливості
  { name: "рівень кешування",        pushes: [{ attr: "швидкодія", dir: 1 }, { attr: "вартість", dir: -1 }] },   // компроміс без двох ваг
];

const views: View[] = [
  { name: "Контекст",    frames: ["вартість", "безпека"] },
  { name: "Контейнери",  frames: ["швидкодія", "доступність"] },
  { name: "Розгортання", frames: ["доступність", "безпека"] },
  { name: "Сценарії",    frames: ["доступність", "швидкодія", "безпека", "вартість"] },
];

function analyse(reg: Stakeholder[], decisions: Decision[], params: Parameter[], views: View[]): void {
  console.log("ВАГОМІСТЬ І КУДИ СПРЯМУВАТИ УВАГУ");
  for (const s of reg)
    console.log(`  ${s.name.padEnd(12)} ${salienceClass(s).padEnd(13)} → ${quadrant(s)}`);

  console.log("\nНЕЗАКРИТІ ТУРБОТИ");
  for (const g of coverageGaps(reg, decisions))
    console.log(`  ${g.veto ? "ВЕТО " : "warn "} ${g.who.padEnd(10)} дбає про ${g.concern} (осей: ${g.score})`);

  console.log("\nТОЧКИ КОМПРОМІСУ");
  for (const t of tradeoffPoints(reg, params))
    console.log(`  «${t.param}»: ${t.up.who}(${t.up.attr} ↑) проти ${t.down.who}(${t.down.attr} ↓)`);

  console.log("\nМАТРИЦЯ В'Ю — порожні рядки");
  const empty = emptyRows(viewMatrix(reg, views));
  if (empty.length === 0) console.log("  усі рядки закриті");
  else for (const i of empty) console.log(`  ✗ ${reg[i].name} (${reg[i].concern}) — жодне в'ю не показує`);
}

analyse(reg, decisions, params, views);
