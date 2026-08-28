#include <stdint.h>
#include <stdbool.h>

#define REG_BC_STATUS 0x01
#define REG_BC_CTRL   0x02

typedef enum {
    PORT_UNKNOWN = 0,
    PORT_SDP     = 1,
    PORT_CDP     = 2,
    PORT_DCP     = 3,
    PORT_APPLE   = 4,
    PORT_SAMSUNG = 5
} usb_port_type_t;

extern uint8_t i2c_read_reg(uint8_t reg);
extern void i2c_write_reg(uint8_t reg, uint8_t val);
extern void charger_set_input_current_limit(uint16_t current_ma);
extern void usb_stack_enable_data(bool enable);

void bc12_interrupt_handler(void)
{
    uint8_t status = i2c_read_reg(REG_BC_STATUS);
    bool vbus_valid = (status & (1 << 7)) != 0;
    bool done = (status & (1 << 0)) != 0;

    if (!vbus_valid) {
        charger_set_input_current_limit(0);
        usb_stack_enable_data(false);
        return;
    }

    if (done) {
        uint8_t port_code = (status >> 4) & 0x07;
        switch (port_code) {
            case PORT_SDP:
                charger_set_input_current_limit(500);
                usb_stack_enable_data(true);
                break;
            case PORT_CDP:
                charger_set_input_current_limit(1500);
                usb_stack_enable_data(true);
                break;
            case PORT_DCP:
                charger_set_input_current_limit(1500);
                usb_stack_enable_data(false);
                break;
            case PORT_APPLE:
                charger_set_input_current_limit(2400);
                usb_stack_enable_data(false);
                break;
            case PORT_SAMSUNG:
                charger_set_input_current_limit(2000);
                usb_stack_enable_data(false);
                break;
            default:
                charger_set_input_current_limit(100);
                usb_stack_enable_data(false);
                break;
        }
    }
}
