// ESP32 (Arduino BLE): сервіс оточення + характеристика температури
BLEServer*         server = BLEDevice::createServer();
BLEService*        env    = server->createService((uint16_t)0x181A);   // Environmental Sensing

BLECharacteristic* temp = env->createCharacteristic(
    (uint16_t)0x2A6E,                                   // Temperature
    BLECharacteristic::PROPERTY_READ |                  // дозволяємо читати
    BLECharacteristic::PROPERTY_NOTIFY);               // ...і сповіщати
temp->addDescriptor(new BLE2902());                    // CCCD — без нього notify мовчить

env->start();
BLEDevice::startAdvertising();                          // почали рекламувати себе
