// Найпростіша "розмова" з контролером: дозволити пуск і дочекатися PG.
// EN — вихід МК на ніжку дозволу; PG — вхід МК від power-good (open-drain + підтяжка).
#define HS_EN   25   // ніжка "дозвіл пуску" контролера
#define HS_PG   26   // ніжка power-good (HIGH = шина встала)
#define HS_FLT  27   // ніжка fault   (LOW  = сталася аварія, open-drain)

bool hotswap_power_up(uint32_t timeout_ms)
{
    gpio_set(HS_EN);                       // дозволили пуск; далі контролер веде затвор сам
    uint32_t t0 = millis();
    while (!gpio_get(HS_PG)) {             // чекаємо, поки вихід доросте до робочого
        if (gpio_get(HS_FLT) == 0)        // аварія під час пуску (коротке / перевантаження)
            return false;                 // ключ уже закрито контролером — далі не йдемо
        if (millis() - t0 > timeout_ms)   // вихід так і не встав за відведений час
            return false;
    }
    return true;                          // PG активний — шина готова, вмикаємо решту плати
}
