const EVENTS: DomainEvent[] =
  Array.from({ length: 10 }, (_, i) => ({ kind: "guest-unlocked", deviceId: "lock-front", at: i }));

// пустити ті самі 10 подій ЧЕРГОЮ на названих споживачів — і порахувати, хто скільки дістав
function throughQueue(consumers: string[]): Record<string, number> {
  const q = new Queue<DomainEvent>();
  const seen: Record<string, number> = {};
  for (const name of consumers) { seen[name] = 0; q.subscribe(() => { seen[name]++; }); }
  for (const e of EVENTS) q.send(e);
  return seen;
}

// те саме, але ТЕМОЮ
function throughTopic(consumers: string[]): Record<string, number> {
  const t = new Topic<DomainEvent>();
  const seen: Record<string, number> = {};
  for (const name of consumers) { seen[name] = 0; t.subscribe(() => { seen[name]++; }); }
  for (const e of EVENTS) t.publish(e);
  return seen;
}

console.log("ЧЕРГА, лише пуш:", throughQueue(["push"]));
console.log("ЧЕРГА, + аудит: ", throughQueue(["push", "audit"]));
console.log("ТЕМА,  + аудит: ", throughTopic(["push", "audit"]));
