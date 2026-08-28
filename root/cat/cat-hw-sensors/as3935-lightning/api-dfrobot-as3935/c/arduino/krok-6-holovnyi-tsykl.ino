void loop() {
  if (!irqTriggered) return;          // подій немає — нічого не робимо
  irqTriggered = false;               // скинути прапорець одразу

  delay(2);                           // ← КРИТИЧНО: дати чіпу досипати

  uint8_t src = lightning.getInterruptSrc();

  if (src == 1) {                     // 1 = блискавка
    uint8_t  distKm = lightning.getLightningDistKm();
    uint32_t energy = lightning.getStrikeEnergyRaw();

    Serial.print("БЛИСКАВКА! відстань ~");
    if (distKm == 1) {
      Serial.println("гроза прямо над головою (поза шкалою)");
    } else if (distKm == 63) {
      Serial.println("надто далеко для оцінки (за межею)");
    } else {
      Serial.print(distKm); Serial.println(" км до фронту грози");
    }
    Serial.print("енергія розряду (сире число): ");
    Serial.println(energy);

  } else if (src == 2) {             // 2 = завада від техніки
    Serial.println("Завада (disturber) — поруч щось шумить");

  } else if (src == 3) {             // 3 = зависокий шум
    Serial.println("Шум зависокий — підніми поріг або віднеси давач");

  } else {                           // 0 = неочікувано
    Serial.println("Переривання без зрозумілої причини");
  }
}
