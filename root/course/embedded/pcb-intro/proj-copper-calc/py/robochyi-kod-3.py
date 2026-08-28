# Струм (А), який пропускає ОДИН via заданого розміру при перегріві dT.
#   drill_mm, plating_um — геометрія отвору
#   delta_t_c            — допустимий перегрів, °C
#   external             — True: рахувати із зовнішнім k (оптимістично);
#                          False: внутрішній k (обережно, за замовчуванням)
# Повертає струм на via в амперах, або -1.0 при некоректних аргументах.
def via_current_a(drill_mm, plating_um, delta_t_c, external):
    if delta_t_c <= 0.0:
        return -1.0
    area = via_barrel_area_mils2(drill_mm, plating_um)
    if area < 0.0:
        return -1.0                        # прокинути помилку розмірів

    k = IPC_K_EXTERNAL if external else IPC_K_INTERNAL
    return ipc2221_current(area, delta_t_c, k)
