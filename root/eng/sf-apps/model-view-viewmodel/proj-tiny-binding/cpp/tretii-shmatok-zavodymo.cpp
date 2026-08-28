// ── 3. Модель подання й дві прив'язки ──
int main() {
    Property<double> temperature{22.0};
    Property<std::string> error;

    temperature.on([&error](const double& t) {          // правило межі — звичайний підписник
        error.set(t >= 5.0 && t <= 30.0 ? std::string{} : std::string{"дозволено 5…30"});
    });

    TextField tempField, errorField;
    {
        Binding<double> b1(tempField, temperature, numToText, textToNum);
        Binding<std::string> b2(errorField, error,
                                [](const std::string& v) { return v; },
                                [](const std::string& s) { return s; });

        temperature.set(35.0);        // tempField.text == "35", errorField.text == "дозволено 5…30"
        tempField.typeIn("12");       // temperature.get() == 12, errorField.text == ""
    }                                 // ← деструктори зняли обидва зв'язки

    temperature.set(99.0);            // поля вже нікого не слухають: у tempField лишилось «12»
}
