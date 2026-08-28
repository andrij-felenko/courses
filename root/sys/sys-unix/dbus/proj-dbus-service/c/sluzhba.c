#include <systemd/sd-bus.h>
#include <stdio.h>
#include <string.h>

#define SVC_NAME  "org.example.Counter"
#define SVC_PATH  "/org/example/Counter"
#define SVC_IFACE "org.example.Counter1"

typedef struct { sd_bus *bus; int64_t value, threshold; } Counter;

/* метод Add: додає крок, повертає нове значення, за потреби б'є на сполох */
static int method_add(sd_bus_message *m, void *userdata, sd_bus_error *ret_error) {
    Counter *c = userdata;
    int64_t step, before;
    int r;

    r = sd_bus_message_read(m, "x", &step);      /* «x» — 64-бітове зі знаком */
    if (r < 0)
        return r;                                /* тіло не збіглося з сигнатурою */

    if (step == 0)                               /* іменована помилка, яку клієнт розрізнить */
        return sd_bus_error_set_const(ret_error, SVC_IFACE ".ZeroStep",
                                      "Крок 0 нічого не змінює");

    before = c->value;
    c->value += step;

    /* стандартний сигнал про зміну властивості — його чекають чужі клієнти */
    sd_bus_emit_properties_changed(c->bus, SVC_PATH, SVC_IFACE, "Value", NULL);

    if (before < c->threshold && c->value >= c->threshold)
        sd_bus_emit_signal(c->bus, SVC_PATH, SVC_IFACE, "Threshold", "x", c->value);

    return sd_bus_reply_method_return(m, "x", c->value);
}

/* читач властивості: пише значення просто у вже приготовану відповідь */
static int prop_value(sd_bus *bus, const char *path, const char *iface,
                      const char *prop, sd_bus_message *reply,
                      void *userdata, sd_bus_error *ret_error) {
    Counter *c = userdata;
    return sd_bus_message_append(reply, "x", c->value);
}

static const sd_bus_vtable counter_vtable[] = {
    SD_BUS_VTABLE_START(0),
    SD_BUS_METHOD_WITH_ARGS("Add",
        SD_BUS_ARGS("x", step), SD_BUS_RESULT("x", value),
        method_add, SD_BUS_VTABLE_UNPRIVILEGED),
    SD_BUS_PROPERTY("Value", "x", prop_value, 0,
        SD_BUS_VTABLE_PROPERTY_EMITS_CHANGE),
    SD_BUS_SIGNAL_WITH_ARGS("Threshold", SD_BUS_ARGS("x", value), 0),
    SD_BUS_VTABLE_END
};
