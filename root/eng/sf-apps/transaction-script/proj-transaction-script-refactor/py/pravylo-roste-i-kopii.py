# place_order — сюди правило додали першим, повністю
net = product.price * qty * (1 - discount)
if net < region_floor(region): net = region_floor(region)   # поріг: є
total = net * (1 + region_tax(region))                      # податок: є

# change_qty — переносили другим, поріг ЗАБУЛИ
net2 = line.price * new_qty * (1 - discount)
total2 = net2 * (1 + region_tax(region))                    # податок: є, поріг: НЕМАЄ

# reorder — руки не дійшли: стара формула, БЕЗ податку й порогу
total3 = line.price * qty * (1 - discount)                  # ані податку, ані порогу
