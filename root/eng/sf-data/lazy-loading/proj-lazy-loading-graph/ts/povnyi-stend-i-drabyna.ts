function scenarioNaive(): number {
  const db = new Db();
  const orders = db.findAllOrders().map((r) => new OrderLazyField(db, r));
  for (const o of orders) void o.customer.name;
  return db.queries;
}
function scenarioIdentityMap(): number {
  const db = new Db();
  const imap = new IdentityMap(db);
  for (const r of db.findAllOrders()) void imap.customer(r.customerId).name;
  return db.queries;
}
function scenarioBatch(): number {
  const db = new Db();
  const rows = db.findAllOrders();
  const customers = db.findCustomers(rows.map((r) => r.customerId));
  for (const r of rows) void customers.get(r.customerId)!.name;
  return db.queries;
}
function scenarioJoin(): number {
  const db = new Db();
  for (const row of db.findOrdersJoinCustomer()) void (row.customer as Row).name;
  return db.queries;
}

console.log("запитів  стратегія");
for (const [run, name] of [
  [scenarioNaive,        "ліниво в циклі"],
  [scenarioIdentityMap,  "+ мапа тотожності"],
  [scenarioBatch,        "пакетний IN-запит"],
  [scenarioJoin,         "жадібний JOIN"],
] as [() => number, string][]) {
  console.log(`${String(run()).padStart(7)}  ${name}`);
}
