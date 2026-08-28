for (const sys of [plainCrud, crudCqrs, esSingle, esCqrs]) {
  sys.send({ kind: "lock",   actor: "Аня",   at: 900 });
  sys.send({ kind: "unlock", actor: "гість", at: 1500 });
  sys.send({ kind: "lock",   actor: "Аня",   at: 1800 });
  console.log(sys.view());
}
// plainCrud → { status: "ЗАЧИНЕНО", lastActor: "Аня", unlockedToday: -1 }
// crudCqrs  → { status: "ЗАЧИНЕНО", lastActor: "Аня", unlockedToday:  1 }
// esSingle  → { status: "ЗАЧИНЕНО", lastActor: "Аня", unlockedToday: -1 }
// esCqrs    → { status: "ЗАЧИНЕНО", lastActor: "Аня", unlockedToday:  1 }
