const uint8_t AO = A0;
const int DRY_ENTER = 800;          // вище цього вважаємо «сухо»
const int WET_ENTER = 500;          // нижче цього вважаємо «дощ»
//   ЗВЕРНІТЬ УВАГУ: DRY_ENTER > WET_ENTER — між ними «мертва зона» гістерезису

bool raining = false;

void setup() {
    Serial.begin(9600);
}

void loop() {
    int v = analogRead(AO);         // менше число = мокріше

    // двопороговий гістерезис прямо на числі:
    //   у «дощ» переходимо, лише впавши НИЖЧЕ WET_ENTER;
    //   у «сухо» — лише піднявшись ВИЩЕ DRY_ENTER.
    if (!raining && v < WET_ENTER) raining = true;
    if ( raining && v > DRY_ENTER) raining = false;

    Serial.print("AO = "); Serial.print(v);
    Serial.println(raining ? "  → дощ" : "  → сухо");
    delay(200);
}
