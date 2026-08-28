void gpio_set_output(GPIO_TypeDef *port, unsigned pin)
{
    port->MODER &= ~(3u << (pin * 2));
    port->MODER |=  (1u << (pin * 2));
}

void gpio_write(GPIO_TypeDef *port, unsigned pin, bool on)
{
    port->BSRR = on ? (1u << pin)          /* молодша половина — звести  */
                    : (1u << (pin + 16));  /* старша половина — скинути  */
}

bool gpio_read(const GPIO_TypeDef *port, unsigned pin)
{
    return (port->IDR >> pin) & 1u;
}
