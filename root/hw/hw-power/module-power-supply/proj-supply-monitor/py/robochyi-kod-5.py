from collections import namedtuple

# Кроки послідовності живлення: вивід ключа + скільки чекати стабілізації.
Stage = namedtuple("Stage", ("sw_pin", "settle_ms"))

STAGES = (
    Stage(LOADSW_SENSOR, 5),    # 1) давач — малий кидок, вмикаємо першим
    Stage(LOADSW_RADIO,  10),   # 2) радіо — найненажерливіше, останнім
)

def all_loadsw_off():
    for st in STAGES:
        gpio_write(st.sw_pin, 0)               # погасити всі гілки

# Увімкнути підпорядковані вузли по черзі, звіряючи рейку після кожного.
# Повертає True, якщо вся послідовність піднялась без просідання.
def power_bringup():
    for st in STAGES:
        gpio_write(st.sw_pin, 1)               # увімкнути чергову гілку
        delay_ms(st.settle_ms)                 # дати конденсаторам зарядитись
        pwr_monitor_step(adc_read(CH_VREFINT)) # свіжий замір рейки

        if not pwr_heavy_ok():          # рейка просіла від кидка цього вузла
            all_loadsw_off()            # ГОНКА: гасимо все, не лізем далі
            return False                # хай викличник зачекає й пробує знову
    return True                         # усі вузли підняті, рейка тримається
