def show(premises, conclusion):
    valid, cx = check(premises, conclusion)
    arg = '%s  ⊢  %s' % (', '.join(premises), conclusion)
    if valid:
        print('ЧИННИЙ    ' + arg)
    else:
        w = ', '.join('%s=%s' % (k, 'І' if v else 'Х') for k, v in sorted(cx.items()))
        print('НЕЧИННИЙ  %s   контрприклад: %s' % (arg, w))

tests = [
    (['p ⟹ q', 'p'], 'q'),                 # модус поненс
    (['p ⟹ q', '¬q'], '¬p'),               # модус толленс
    (['p ⟹ q', 'q'], 'p'),                 # ХИБА: ствердження висновку
    (['p ⟹ q', '¬p'], '¬q'),               # ХИБА: заперечення посилки
    (['p ∨ q', '¬p'], 'q'),                 # диз'юнктивний силогізм
    (['p ⟹ q', 'q ⟹ r'], 'p ⟹ r'),         # транзитивність імплікації
    (['p ∨ q', 'p ⟹ r', 'q ⟹ r'], 'r'),    # розбір випадків
]
for prem, con in tests:
    show(prem, con)

print('---')
show([], 'p ∨ ¬p')          # порожні посилки: чинність = висновок є тавтологією
show([], 'p ∨ q')           # не тавтологія → нечинний
show(['p', '¬p'], 'q')      # суперечливі посилки доводять будь-що
