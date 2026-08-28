// Пріоритет failsafe-реакцій: більше число — вища терміновість.
// Спрацьовує НАЙВИЩА з активних умов, решта чекають.
typedef enum {
    FS_NONE       = 0,
    FS_GEOFENCE   = 1,   // наближення до забороненої зони: розвернути/зависнути
    FS_LINK_LOST  = 2,   // втрата зв'язку: повернутися додому
    FS_LOW_BATT   = 3,   // критичний заряд: сідати негайно тут
    FS_CRITICAL   = 4,   // відмова, що загрожує падінням: керована аварійна посадка
} failsafe_level_t;

// Обираємо єдину реакцію з усіх активних умов — найвищу за пріоритетом.
failsafe_level_t failsafe_arbitrate(int near_geofence, int link_lost,
                                    int batt_critical, int hw_failure) {
    if (hw_failure)     return FS_CRITICAL;   // падаємо — усе інше вже не важить
    if (batt_critical)  return FS_LOW_BATT;   // сядемо тут, бо додому не дотягнемо
    if (link_lost)      return FS_LINK_LOST;  // додому, поки є заряд
    if (near_geofence)  return FS_GEOFENCE;   // найм'якша: просто не пускаємо за межу
    return FS_NONE;
}
