def submerged_volume_by_profile(d, area_of_depth, n=2000):
    """Витіснений об'єм для БУДЬ-ЯКОГО профілю A(z) — метод трапецій."""
    step = d / n
    s = 0.5 * (area_of_depth(0.0) + area_of_depth(d))
    for i in range(1, n):
        s += area_of_depth(i * step)
    return s * step

area = lambda z: math.pi * z * (2 * R - z)          # переріз кулі на глибині z
print(submerged_volume_by_profile(d, area))         # 2.513274e-03
print(sphere_submerged_volume(d, R))                # 2.513274e-03 — збіг
