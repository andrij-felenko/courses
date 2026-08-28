// Приклад: у момент зльоту запам'ятати «нуль», далі рахувати відносну висоту.
static float ground_pressure_pa = 101325.0f;   // оновимо на старті

void bmp180_set_ground_level() {
  // усереднити кілька вимірів, щоб «нуль» був стабільним
  int32_t sum = 0;
  for (int i = 0; i < 16; i++) { sum += bmp180_pressure(); delay(10); }
  ground_pressure_pa = sum / 16.0f;
}

float bmp180_relative_altitude() {
  return bmp180_altitude(bmp180_pressure(), ground_pressure_pa);
}
