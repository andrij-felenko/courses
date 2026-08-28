interface Device {                    // доменний пристрій із реєстру — тепер з ключем
  id: string;                         // стабільний ідентифікатор, напр. "lock-1"
  kind: string;                       // "lock", "plug", "thermostat"…
  room: string;
  state: string;
}

interface DeviceRepository {          // ПОРТ: три обіцянки, і жодного слова про носій
  save(d: Device): void;              // поклади (або онови за id)
  get(id: string): Device | undefined;// дай один за ключем, або нічого
  all(): Device[];                    // дай усіх
}
