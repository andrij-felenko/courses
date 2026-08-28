from math import log10

# Поправка на висоту мобільного (середнє місто) — спільна для Hata і COST 231
def a_hm_medium(f, hm):
    return (1.1 * log10(f) - 0.7) * hm \
         - (1.56 * log10(f) - 0.8)


# COST 231-Hata, дБ.  f — МГц (1500..2000), hb — м (30..200),
# hm — м (1..10), d — км (1..20), big_city — True для метрополії
def cost231_db(f, hb, hm, d, big_city):
    Cm = 3.0 if big_city else 0.0
    return (46.3
            + 33.9 * log10(f)
            - 13.82 * log10(hb)
            - a_hm_medium(f, hm)
            + (44.9 - 6.55 * log10(hb)) * log10(d)
            + Cm)


L = cost231_db(1800.0, 30.0, 1.5, 2.0, big_city=True)
# L ≈ 149.8 дБ — порівняй із міською Hata на 900 МГц/2 км (≈137 дБ):
# подвоєння частоти + метрополія додають ще ~12.8 дБ втрат.
