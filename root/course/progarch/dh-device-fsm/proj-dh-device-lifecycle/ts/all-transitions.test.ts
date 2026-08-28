// all-transitions.test.ts — пробігає ВСІ 4×4 пари й доводить: незаконна кидає,
// законна веде РІВНО в очікуваний стан з однією подією, no-op — тихий і без події.
import assert from "node:assert/strict";

const STATES: DeviceStatus[] = ["new", "online", "offline", "retired"];
const CMDS: Command[] = ["commission", "markOffline", "markOnline", "retire"];

// Привести свіжий пристрій у заданий стан ЛИШЕ законними командами.
function deviceIn(s: DeviceStatus): Device {
  const d = new Device("dut");                              // dut — device under test
  if (s !== "new") d.commission("home-1");
  if (s === "offline" || s === "retired") d.markOffline();
  if (s === "retired") d.retire();
  return d;
}
function invoke(d: Device, c: Command): void {
  switch (c) {
    case "commission":  return d.commission("home-9");
    case "markOffline": return d.markOffline();
    case "markOnline":  return d.markOnline();
    case "retire":      return d.retire();
  }
}

for (const s of STATES) for (const c of CMDS) {
  const legal = TRANSITIONS.get(key(s, c));                 // очікуваний перехід або undefined
  const noop  = IDEMPOTENT.get(c) === s;                    // ідемпотентний повтор?
  const d = deviceIn(s);
  d.pullEvents();                                           // відкинути події налаштування

  if (legal !== undefined) {
    invoke(d, c);
    assert.equal(d.state, legal, `${s}×${c}: мав перейти в ${legal}`);
    assert.equal(d.pullEvents().length, 1, `${s}×${c}: рівно одна подія на перехід`);
  } else if (noop) {
    invoke(d, c);
    assert.equal(d.state, s, `${s}×${c}: no-op не міняє стан`);
    assert.equal(d.pullEvents().length, 0, `${s}×${c}: no-op не емітить події`);
  } else {
    assert.throws(() => invoke(d, c), DomainError, `${s}×${c}: мав кинути`);
    assert.equal(d.state, s, `${s}×${c}: після кидка стан незмінний`);
    assert.equal(d.pullEvents().length, 0, `${s}×${c}: збій не лишає події`);
  }
}
console.log(`покрито ${STATES.length * CMDS.length} пар (стан × команда) ✓`);

// ── Золоті випадки: намір дому, записаний НЕЗАЛЕЖНО від таблиці (див. пастки).
assert.throws(() => new Device("x").retire(), DomainError);         // невведений не списують
{ const d = deviceIn("retired"); assert.throws(() => d.markOnline(), DomainError); }  // мертвий не оживе
{ const d = deviceIn("online"); d.pullEvents(); d.markOnline();      // повтор online
  assert.equal(d.pullEvents().length, 0); }                         // no-op не спамить Reconnected
