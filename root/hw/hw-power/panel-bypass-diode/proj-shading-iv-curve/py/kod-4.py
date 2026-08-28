# друк: точка елемента, ВАХ, горби, порівняння трекерів
ic = np.linspace(0, Iph - 1e-6, 5000)
vc = cell_V(ic, Iph); mp = int((vc * ic).argmax())
print("Один елемент:  Voc = %.3f В   Vmp = %.3f В   Imp = %.2f А   (Iph = %.1f А)"
      % (cell_V(np.array([0.0]), Iph)[0], vc[mp], ic[mp], Iph))

print("\n  I, А   V, В    P, Вт")
for Iq in [0.5, 1.0, 2.0, 2.9, 3.1, 4.0, 5.0, 5.9, 6.1, 7.0, 8.0, 8.5, 8.9]:
    Vq = float(sum(subrow_V(np.array([Iq]), s) for s in subrows)[0])
    print("  %4.1f  %5.1f  %6.1f" % (Iq, Vq, Vq * Iq))

print("\nЛокальні максимуми (горби кривої):")
for i in local_maxima(P):
    print("  V = %5.1f В   I = %4.2f А   P = %6.1f Вт" % (V[i], I[i], P[i]))

g = int(P.argmax())          # глобальний максимум — суцільний перебір
h = hill_climb(P)            # локальний — простий трекер від холостого ходу
print("\nГлобальний максимум:               P = %6.1f Вт   (V = %.1f В)" % (P[g], V[g]))
print("Hill-climbing від холостого ходу:  P = %6.1f Вт   (V = %.1f В)" % (P[h], V[h]))
print("Недобір потужності:                %.0f %%" % (100 * (P[g] - P[h]) / P[g]))
