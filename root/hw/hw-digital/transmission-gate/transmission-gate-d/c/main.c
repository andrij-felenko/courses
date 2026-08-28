#include <stdio.h>
#include <stdbool.h>

/* Стан логічного вузла: активні рівні або високий імпеданс Hi-Z */
typedef enum {
    LOGIC_0,
    LOGIC_1,
    LOGIC_WEAK_1, /* Деградована одиниця одиночного NMOS (Vdd - Vth) */
    LOGIC_WEAK_0, /* Деградований нуль одиночного PMOS (|Vthp|) */
    LOGIC_HIZ
} LogicState;

/* Модель одиночного NMOS-ключа */
LogicState nmos_pass_switch(LogicState in, bool gate_enable) {
    if (!gate_enable) return LOGIC_HIZ;
    if (in == LOGIC_0) return LOGIC_0;           /* NMOS чудово проводить сильний 0 */
    if (in == LOGIC_1) return LOGIC_WEAK_1;      /* NMOS втрачає поріг на одиниці */
    return in;
}

/* Модель CMOS передавального вентиля (TG) */
LogicState cmos_transmission_gate(LogicState in, bool en) {
    /* en=true означає EN=1 і EN_bar=0 (обидва транзистори відкриті) */
    if (!en) return LOGIC_HIZ;
    
    /* Паралельна пара передає сильний 0 через NMOS і сильну 1 через PMOS */
    return in;
}

int main(void) {
    printf("--- Тестування одиночного NMOS проти CMOS TG ---\n");
    
    printf("NMOS(Вхід 0, EN=1) -> %s\n", nmos_pass_switch(LOGIC_0, true) == LOGIC_0 ? "Сильний 0" : "Помилка");
    printf("NMOS(Вхід 1, EN=1) -> %s\n", nmos_pass_switch(LOGIC_1, true) == LOGIC_WEAK_1 ? "Квола 1 (Vdd - Vth)" : "Помилка");
    
    printf("CMOS_TG(Вхід 0, EN=1) -> %s\n", cmos_transmission_gate(LOGIC_0, true) == LOGIC_0 ? "Сильний 0 (0 В)" : "Помилка");
    printf("CMOS_TG(Вхід 1, EN=1) -> %s\n", cmos_transmission_gate(LOGIC_1, true) == LOGIC_1 ? "Сильна 1 (Vdd)" : "Помилка");
    printf("CMOS_TG(Вхід 1, EN=0) -> %s\n", cmos_transmission_gate(LOGIC_1, false) == LOGIC_HIZ ? "Hi-Z (Ізольовано)" : "Помилка");
    
    return 0;
}
