pulses = 0                              # лічить ISR, читає loop()

def on_pulse(pin):                      # ISR: коротко — лише інкремент
    global pulses
    pulses += 1

def loop():
    state = machine.disable_irq()
    p = pulses                          # знімок цілого значення
    machine.enable_irq(state)
    # далі працюємо з копією p, а не з живою pulses
