from time import sleep
import os

def tick(device: Device, heating: bool) -> bool:
    t = device.temperature()          # read
    heating = should_heat(t, heating) # decide — чисте правило, байдуже до заліза
    device.heat(heating)              # act
    return heating

def run(device: Device) -> None:      # прод: вічний цикл, точнісінько як серце v0
    heating = False
    while True:
        heating = tick(device, heating)
        sleep(30)

def build_device() -> Device:         # ТОЧКА ЗБІРКИ — єдине місце, що знає, хто за портом
    if os.getenv("DH_ENV") == "prod":
        return RealDevice("28-0119a1b2c3d4", "http://192.168.1.50")
    return FakeDevice()               # усюди, крім проду, — дім у пам'яті

if __name__ == "__main__":
    run(build_device())               # у проді сюди стане RealDevice — і код вище не здригнеться
