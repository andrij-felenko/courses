// Головна процедура: розгорнути, знайти вікно, повернути його центр.
// Повертає код ручки для посадки, або -1, якщо робочого вікна нема взагалі.
int find_center()
{
    bool map[RANGE_MAX];
    int n = sweep(map, RANGE_MAX);

    Window w = widest_window(map, n);
    if (w.width == 0) {
        return -1;                         // жодної робочої точки — канал мертвий
    }
    return (w.lo + w.hi) / 2;              // центр САМЕ цього вікна
}
