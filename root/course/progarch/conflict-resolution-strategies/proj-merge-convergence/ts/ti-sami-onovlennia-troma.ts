const lwwFrags: LWW[] = [
  { val: new Set(["торшер"]),   ts: 1, node: "A" },   // A: увесь список = {торшер}
  { val: new Set(["гірлянда"]), ts: 1, node: "B" },   // B одночасно: увесь список = {гірлянда}
];
const sibFrags: Version[][] = [
  [{ list: ["торшер"],   vv: { A: 1 } }],
  [{ list: ["гірлянда"], vv: { B: 1 } }],
];
const orFrags: ORSet[] = [
  { add: { торшер:   new Set(["a1"]) }, rem: {} },      // A: +торшер (тег a1)
  { add: { гірлянда: new Set(["b1"]) }, rem: {} },      // B: +гірлянда (тег b1)
  { add: {}, rem: { торшер: new Set(["a1"]) } },        // −торшер, бачив лише тег a1
  { add: { торшер:   new Set(["c1"]) }, rem: {} },      // C: +торшер знову (новий тег c1)
];
