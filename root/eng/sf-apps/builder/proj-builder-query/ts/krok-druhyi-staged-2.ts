// ✓ Проходить: метод → url → (необов'язкові) → build
const ok = httpRequest()
  .method("POST")
  .url("https://api.example.com/orders")
  .body('{"item":"кава"}')
  .build();

// ✗ НЕ КОМПІЛЮЄТЬСЯ: build() нема в стадії NeedUrl
const bad1 = httpRequest()
  .method("POST")
  .build();
//   ~~~~~ Property 'build' does not exist on type 'NeedUrl'.

// ✗ НЕ КОМПІЛЮЄТЬСЯ: header() нема в стартовій стадії NeedMethod —
//    не можна чіпати необов'язкове, поки не задав метод
const bad2 = httpRequest()
  .header("X", "1");
//   ~~~~~~ Property 'header' does not exist on type 'NeedMethod'.

// ✗ НЕ КОМПІЛЮЄТЬСЯ: url() очікує рядок, а не число — звичайна перевірка типу кроку
const bad3 = httpRequest()
  .method("GET")
  .url(123);
//       ~~~ Argument of type 'number' is not assignable to parameter of type 'string'.
