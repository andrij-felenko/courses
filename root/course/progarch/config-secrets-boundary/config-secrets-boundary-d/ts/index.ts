// У конфізі — тільки ПОСИЛАННЯ на секрет, ніколи саме значення.
const manifest = {
  dbHost: "prod-db.internal",                 // звичайний конфіг — так і лежить у файлі
  dbPassword: { secret: "dh/db/password" },   // секрет — лише адреса у сховищі
};

// На старті резолвер міняє посилання на справжнє значення.
async function resolve(m: typeof manifest, store: SecretStore) {
  return {
    dbHost: m.dbHost,
    dbPassword: await store.get(m.dbPassword.secret), // значення з'являється лише тут, у пам'яті
  };
}
// dbPassword не існує ні в git, ні в образі — тільки в цій структурі, тільки після старту.
