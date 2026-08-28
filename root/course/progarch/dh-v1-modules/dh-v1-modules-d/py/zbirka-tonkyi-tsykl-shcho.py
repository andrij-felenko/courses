def run(sensor: Sensor, heater: Heater, cfg: Config):
    while True:
        reading = sensor.read()          # драйвер ховає діалект заліза
        match decide(reading, cfg):      # чисте рішення — саме лише °C усередині
            case Command.HEAT: heater.on()
            case Command.IDLE: heater.off()
        sleep(30)

# єдине місце, де конкретне зустрічає конкретне:
run(sensor=OneWireThermometer(), heater=SmartPlug(), cfg=Config(threshold=20.0))
