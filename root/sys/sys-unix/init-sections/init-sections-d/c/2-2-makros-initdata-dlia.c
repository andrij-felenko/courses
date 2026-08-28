#include <linux/init.h>

/* Великий масив конфігурації, який потрібен лише при старті */
static int initial_port_configuration[1024] __initdata = { 
    [0 ... 1023] = -1 
};

static int __init my_network_driver_init(void)
{
    int i;
    for (i = 0; i < 1024; i++) {
        if (initial_port_configuration[i] != -1) {
            setup_port(i, initial_port_configuration[i]);
        }
    }
    return 0;
}
