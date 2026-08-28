gw = OrderGateway("c-19", 1200.0)   # persisted=False, id=None — рядка ще немає
gw.save()                            # persisted False → INSERT
print(gw.id, gw.persisted)           # 1 True

gw.status = "paid"
gw.save()                            # persisted True → UPDATE (а не другий INSERT!)

again = OrderFinder.find(1)          # persisted True одразу — рядок із бази
again.total = 999.0
again.save()                         # UPDATE

gw.delete()                          # DELETE; далі gw.id=None, gw.persisted=False
