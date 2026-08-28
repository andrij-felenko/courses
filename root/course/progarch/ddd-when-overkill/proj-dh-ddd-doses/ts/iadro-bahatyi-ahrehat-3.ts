import assert from "node:assert/strict";

// 1) Сценарії перемикаються вільно й лишають РІВНО ОДНЕ, не обидва.
const bedroom = new Room("спальня");
bedroom.apply({ name: "Ніч",   climate: { want: "cool", targetC: 18 }, lightsOn: false });
assert.equal(bedroom.climate, "cooling");
bedroom.apply({ name: "Ранок", climate: { want: "heat", targetC: 22 }, lightsOn: true });
assert.equal(bedroom.climate, "heating");        // холод сам згас, коли прийшло гріння

// 2) Два незалежні правила конфліктують — корінь відмовляє, а не мовчить.
const hall = new Room("вітальня");
hall.startHeating(21);                            // правило «надворі холодно»
assert.throws(() => hall.startCooling(24), DomainError);   // правило «волого» — конфлікт!

// 3) На шляху відмови стан НЕ спотворився: досі гріємо, кулер не прокрався.
assert.equal(hall.climate, "heating");
