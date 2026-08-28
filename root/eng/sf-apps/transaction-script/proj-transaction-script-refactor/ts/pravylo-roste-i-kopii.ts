// placeOrder — сюди правило додали першим, повністю
let net = product.price * qty * (1 - discount);
if (net < regionFloor(region)) net = regionFloor(region);   // поріг: є
const total = net * (1 + regionTax(region));                // податок: є

// changeQty — переносили другим, поріг ЗАБУЛИ
let net2 = line.price * newQty * (1 - discount);
const total2 = net2 * (1 + regionTax(region));              // податок: є, поріг: НЕМАЄ

// reorder — руки не дійшли: стара формула, БЕЗ податку й порогу
const total3 = line.price * qty * (1 - discount);           // ані податку, ані порогу
