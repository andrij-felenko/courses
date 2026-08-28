# Викликається регулярно з польотного циклу.
# Спершу — найнебезпечніше (батарея), потім — власне геозона.

def fence_check(lat, lon, alt_m):
    if inside_cylinder(lat, lon, alt_m):
        return                           # усе гаразд, апарат у межах

    # Ми ЗА межею. Але спершу — чи вистачить ресурсу на повернення?
    if battery_critical():
        set_mode(MODE_LAND)              # додому не дотягнемо — сідаємо тут
        return
    set_mode(MODE_RTL)                   # інакше — повертаємось у зону
