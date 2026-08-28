// очікуваний код АЦП для середини шкали без навантаження
const float V_supply = 3.3f;
const int   ADC_MAX  = 4095;

int expected = (int)((V_supply * 0.5f / V_supply) * ADC_MAX); // = 2047
int measured = analogRead(POT_PIN);

// велике розходження = повзунок навантажений, треба буфер
if (abs(measured - expected) > 200) {
    // ставимо ОП-повторювач або беремо пот меншого опору
}
