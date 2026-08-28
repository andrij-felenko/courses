void digitalWrite(uint8_t pin, uint8_t val) {
  uint8_t timer = digitalPinToTimer(pin);   // а раптом на цьому піні ШІМ?
  uint8_t bit   = digitalPinToBitMask(pin);  // яка це ніжка порту (маска біта)?
  uint8_t port  = digitalPinToPort(pin);     // якого саме порту (B, C, D)?
  volatile uint8_t *out = portOutputRegister(port);

  if (timer != NOT_ON_TIMER) turnOffPWM(timer);  // якщо ШІМ — вимкнути його

  uint8_t oldSREG = SREG;   // зберегти стан переривань
  cli();                    // заборонити переривання (щоб запис був цілісним)
  if (val == LOW)  *out &= ~bit;
  else             *out |=  bit;
  SREG = oldSREG;           // відновити переривання
}
