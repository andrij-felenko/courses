// allowed[from][to] == true  ⟺  перехід from→to дозволений.
// Усе, чого тут немає, — НЕЛЕГАЛЬНЕ й буде відкинуте функцією переходу.
static const bool allowed[ST_COUNT][ST_COUNT] = {
//              BOOT  READY ARMED FLY   LAND  DISARM
/* BOOT   */  { 0,    1,    0,    0,    0,    0 },  // самоперевірка → READY
/* READY  */  { 0,    0,    1,    0,    0,    0 },  // ARM → ARMED
/* ARMED  */  { 0,    1,    0,    1,    0,    0 },  // роззброїтись назад / зліт
/* FLYING */  { 0,    0,    0,    0,    1,    0 },  // місію виконано / RTL → LANDING
/* LANDING*/  { 0,    0,    0,    1,    0,    1 },  // сіло → DISARM; зірвати посадку → FLYING
/* DISARM */  { 0,    1,    0,    0,    0,    0 },  // після паузи можна знову READY
};
