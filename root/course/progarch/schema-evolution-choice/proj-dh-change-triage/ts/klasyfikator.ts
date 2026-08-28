function chooseEvolutionStrategy(c: DataChange): Decision {
  // 0. ҐВАРДІЯ — перш ніж думати про стратегію. Сенс живого ключа не перепризначають.
  if (c.kind === "redefine")
    return { strategy: "FORBIDDEN", window: "none", backfill: false, compat: "n/a",
      note: "новий сенс = новий ключ/версія; старий ключ лишається старим сенсом" };

  // 1. Похідні дані обходять усю матрицю: не мігруй — перерахуй.
  if (c.derived)
    return { strategy: "REBUILD", window: "none", backfill: false, compat: "n/a",
      note: "зміни функцію зведення, перебудуй вікно із сирого" };

  // 2. Адитивне: старі дані лишаються валідні, backfill сенсу нема.
  if (c.kind === "add")
    return { strategy: "ADD",
      window: c.controlsBothSides ? "short" : "long", backfill: false,
      compat: c.controlsBothSides ? "n/a" : "forward",
      note: "старий читач мусить ІГНОРУВАТИ незнайоме, а не падати на ньому" };

  // 3. Прибирання — це фаза contract чиєїсь давнішої expand.
  if (c.kind === "remove")
    return { strategy: "RETIRE",
      window: c.rewritable ? "short" : "may-never-close", backfill: false,
      compat: "backward",
      note: "гейт: ні писаря, ні ДОСЯЖНОГО збереженого запису на старій формі" };

  // 4. reshape справжнього джерела правди — вирішує вісь переписуваності.
  if (!c.rewritable)
    return { strategy: "SCHEMA_ON_READ",
      window: c.controlsBothSides ? "grows-with-decoder" : "may-never-close",
      backfill: false,
      compat: c.controlsBothSides ? "backward" : "backward+forward",
      note: "тегай кожен запис версією, зводь на читанні; історію не переписуй" };

  return { strategy: "MIGRATE_IN_PLACE",
    window: c.controlsBothSides ? "short" : "long", backfill: true,
    compat: c.controlsBothSides ? "backward" : "backward+forward",
    note: "expand → backfill пакетами → contract" };
}
