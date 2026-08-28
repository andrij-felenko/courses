# Кремнієва межа: Ron·A [Ом·см²] = 8.3e-9 · BV^2.5
def si_ron_a(bv_volts):
    return 8.3e-9 * bv_volts ** 2.5   # Ом·см²


BV      = 600.0    # робоча напруга, В
Rds_max = 0.050    # бажаний опір, Ом (50 мОм)

ronA_si = si_ron_a(BV)        # Ом·см² на межі кремнію
area_si = ronA_si / Rds_max   # потрібна площа: A = Ron·A / R
print(f"Si: Ron*A = {ronA_si:.4f} Ом*см^2,  площа = {area_si:.3f} см^2")

# SiC: приблизно у 340 разів менший питомий опір -> у 340 разів менша площа
ronA_sic = ronA_si / 340.0
area_sic = ronA_sic / Rds_max
print(f"SiC: Ron*A = {ronA_sic:.5f} Ом*см^2, площа = {area_sic:.4f} см^2")

print(f"Виграш за площею: {area_si / area_sic:.0f}x")
