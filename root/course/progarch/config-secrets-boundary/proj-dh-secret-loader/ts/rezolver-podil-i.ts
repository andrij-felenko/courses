type Resolved = Record<string, string | number | boolean | Secret>;

// Поділ + підстановка: просте лишаємо як є, посилання міняємо на Secret.
// Секрети тягнемо ПАРАЛЕЛЬНО, на старті, один раз.
async function resolve(m: Record<string, Leaf>, store: SecretStore): Promise<Resolved> {
  const entries = await Promise.all(
    Object.entries(m).map(async ([key, val]) =>
      [key, isRef(val) ? new Secret(await store.get(val.secret)) : val] as const),
  );
  return Object.fromEntries(entries);
}
