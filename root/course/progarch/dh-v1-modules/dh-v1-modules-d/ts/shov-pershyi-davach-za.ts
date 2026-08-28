interface Reading {
  readonly celsius: number;   // ЗАВЖДИ °C: одиниця в контракті, не в голові
  readonly ok: boolean;       // чи вдалося дістати справжнє свіже число
}

interface Sensor {            // ПОРТ: рішення залежить від цього, а не від марки заліза
  read(): Reading;
}

class OneWireThermometer implements Sensor {   // мову свого давача знає тільки драйвер
  read(): Reading {
    const raw = this.device.millicelsius();     // 20125 — діалект саме цього давача
    return { celsius: raw / 1000, ok: true };   // переклад на °C ТУТ, на самому краю
  }
}
