// Доступ до порту конфігурації — під взаємним виключенням: скрабер і логіка
// НЕ повинні лізти до нього одночасно, інакше зіпсують операцію одне одному.
extern void cfg_port_lock(void);
extern void cfg_port_unlock(void);

// Обгортка: обробити кадр, тримаючи порт замкненим лише на час однієї операції.
static scrub_result_t scrub_one_frame_locked(uint32_t f)
{
    cfg_port_lock();                       // ніхто інший зараз до порту не влізе
    scrub_result_t r = scrub_one_frame(f);
    cfg_port_unlock();                     // відпустили — хай логіка теж попрацює
    return r;
}
