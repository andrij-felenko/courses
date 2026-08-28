o = Order("A-001")
o.pay()       # New → Paid
o.ship()      # Paid → Shipped
o.ship()      # ігнор: повторне відправлення (стан «Shipped») — стан не змінився
o.refund()    # Shipped → Refunded
print(o.state_name)               # "Refunded"

try:
    o.cancel()                    # у Refunded cancel не описаний → заборона з бази
except IllegalTransition as e:
    print(e)
# "не можна скасувати: замовлення у стані «Refunded»"

print(o.logbook)
# ['New → Paid', 'Paid → Shipped',
#  'ігнор: повторне відправлення (стан «Shipped»)',
#  'Shipped → Refunded']
