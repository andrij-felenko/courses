// Ланцюг READY намальовано на аркуші давача й на аркуші MCU
// (два міжаркушеві конектори з тим самим іменем) — електрично це ОДНА мережа,
// заведена на вивід 14 мікроконтролера. У коді вся мережа = один пін.
#define READY_PIN  14            // куди ланцюг READY заходить на аркуші MCU

gpio_set_direction(READY_PIN, GPIO_IN);

bool sensor_ready(void)
{
    return gpio_get_level(READY_PIN) == 1;   // увесь ланцюг READY, через усі аркуші
}
