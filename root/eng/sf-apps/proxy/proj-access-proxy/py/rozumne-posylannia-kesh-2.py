real = RealOrderService()
cached = LoggingCachingOrderService(real)       # облік поверх бази
guarded = ProtectedOrderService(cached, bob)    # охорона поверх обліку

# bob працює через один тип OrderService і не бачить ні охорони, ні кешу, ні бази:
guarded.get_order("ord-42")
# → перевірка права read (ок) → лог → промах кешу → база → у кеш
guarded.get_order("ord-42")
# → перевірка права read (ок) → лог → влучення в кеш → база НЕ чіпається
guarded.cancel_order("ord-42")
# → перевірка права cancel → у bob його немає → AccessDenied, кеш і база цілі
