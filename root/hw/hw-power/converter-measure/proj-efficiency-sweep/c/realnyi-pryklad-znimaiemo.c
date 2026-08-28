#include <stdio.h>      // snprintf

// --- тонкий шар приладу (SCPI текстом у порт) ---
void  port_send(const char *line);          // дописує "\n" і шле в UART
float port_query(const char *line);         // шле запит, парсить число з відповіді

static void psu_set_voltage(float v) { char c[32]; snprintf(c, sizeof c, "VOLT %.3f", v); port_send(c); }
static void load_set_current(float a) { char c[32]; snprintf(c, sizeof c, "CURR %.3f", a); port_send(c); }

// один вузол сітки: повертає ккд у % (або -1 при відмові DUT)
float measure_point(float vin_set, float iout_set, float vout_nom)
{
    psu_set_voltage(vin_set);   port_send("OUTP ON");      // вхід під напругою
    load_set_current(iout_set); port_send("INP ON");       // навантаження тримає струм

    settle_ms(2000);            // ЧЕКАТИ усталення: електрика + тепловий дрейф

    float vin  = port_query("MEAS:VOLT? PSU");   // Kelvin-відбір — окремі дроти на клемах
    float iin  = port_query("MEAS:CURR? PSU");
    float vout = port_query("MEAS:VOLT? LOAD");
    float iout = port_query("MEAS:CURR? LOAD");

    if (vout < vout_nom * 0.9f) {                // вихід просів > 10 % → DUT у захисті/відмові
        port_send("INP OFF");                    // негайно зняти струм, не палити плату
        return -1.0f;
    }
    float pin = vin * iin, pout = vout * iout;
    return (pin > 0.0f) ? (pout / pin) * 100.0f : -1.0f;
}
