import machine

cause = machine.reset_cause()
if cause == machine.PWRON_RESET:
    print("старт: подали живлення / EN")
elif cause == machine.BROWNOUT_RESET:
    print("старт: ПРОСІВ живлення (brownout)!")
elif cause == machine.SOFT_RESET:
    print("старт: програмне перезавантаження")
else:
    print("старт: інша причина")
