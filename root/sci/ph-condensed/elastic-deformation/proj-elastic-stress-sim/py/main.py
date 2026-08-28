import math

class Segment:
    def __init__(self, name, length, diameter, young_modulus, poisson_ratio, alpha=0.0, delta_t=0.0):
        self.name = name
        self.length = length             # L (м)
        self.diameter = diameter         # d (м)
        self.E = young_modulus           # E (Па)
        self.nu = poisson_ratio          # ν
        self.alpha = alpha               # α (1/K)
        self.delta_t = delta_t           # ΔT (K)

def calculate_rod_state(segments, force):
    results = []
    total_delta_l = 0.0
    total_energy = 0.0

    for seg in segments:
        area = math.pi * (seg.diameter ** 2) / 4.0
        stress = force / area
        strain_mech = stress / seg.E
        strain_therm = seg.alpha * seg.delta_t
        strain_total = strain_mech + strain_therm
        
        delta_l = seg.length * strain_total
        delta_d = -seg.nu * strain_mech * seg.diameter
        volume = area * seg.length
        energy = 0.5 * stress * strain_mech * volume

        total_delta_l += delta_l
        total_energy += energy

        results.append({
            "name": seg.name,
            "stress_MPa": stress / 1e6,
            "strain_mech_pct": strain_mech * 100.0,
            "delta_l_mm": delta_l * 1000.0,
            "delta_d_um": delta_d * 1e6,
            "energy_J": energy
        })

    return results, total_delta_l, total_energy

if __name__ == "__main__":
    # Двосегментний стержень (сталь + алюміній) під навантаженням 50 кН
    rod = [
        Segment("Сталевий сегмент", length=0.5, diameter=0.02, young_modulus=210e9, poisson_ratio=0.30),
        Segment("Алюмінієвий сегмент", length=0.3, diameter=0.025, young_modulus=70e9, poisson_ratio=0.33)
    ]
    axial_force = 50000.0  # 50 кН

    res, total_l, total_u = calculate_rod_state(rod, axial_force)

    print(f"=== Результати розрахунку (Сила = {axial_force/1000:.1f} кН) ===")
    for r in res:
        print(f"[{r['name']}]")
        print(f"  Напруження σ:       {r['stress_MPa']:.2f} МПа")
        print(f"  Пружна деформація: {r['strain_mech_pct']:.4f} %")
        print(f"  Подовження ΔL:      {r['delta_l_mm']:.4f} мм")
        print(f"  Зміна діаметра Δd: {r['delta_d_um']:.2f} мкм")
        print(f"  Енергія U:          {r['energy_J']:.4f} Дж")

    print(f"Загальне подовження стержня: {total_l*1000:.4f} мм")
    print(f"Повна потенціальна енергія:   {total_u:.4f} Дж")
