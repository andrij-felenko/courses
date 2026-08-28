OrderService real = new RealOrderService();
OrderService cached = new LoggingCachingOrderService(real);      // облік поверх бази
OrderService guarded = new ProtectedOrderService(cached, bob);   // охорона поверх обліку

// bob працює через один тип OrderService і не бачить ні охорони, ні кешу, ні бази:
guarded.getOrder("ord-42");
// → перевірка права read (ок) → лог → промах кешу → база → у кеш
guarded.getOrder("ord-42");
// → перевірка права read (ок) → лог → влучення в кеш → база НЕ чіпається
guarded.cancelOrder("ord-42");
// → перевірка права cancel → у bob його немає → AccessDenied, кеш і база цілі
