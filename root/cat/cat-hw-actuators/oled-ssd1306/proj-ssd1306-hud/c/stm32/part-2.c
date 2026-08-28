// STM32 / U8g2: велике число посередині, ціле «з комою вручну», без float.
void draw_big_value(int32_t centi) {
  int32_t whole = centi / 100;
  int32_t frac  = centi % 100;
  if (frac < 0) frac = -frac;
  char s[16];
  snprintf(s, sizeof(s), "%ld.%02ld", (long)whole, (long)frac);

  u8g2_ClearBuffer(&u8g2);
  u8g2_SetFont(&u8g2, u8g2_font_logisoso24_tn);  // великий шрифт, лише цифри й «.»
  u8g2_DrawStr(&u8g2, 4, 44, s);                 // (x, baseline_y, текст)
  u8g2_SendBuffer(&u8g2);
}
