// прапорці напряму — у старших бітах результату
#define DIR_NONE 0x00   // цикл ще не завершено
#define DIR_CW   0x10   // завершено крок за годинниковою
#define DIR_CCW  0x20   // завершено крок проти годинникової

// стани самого автомата (проміжні кроки обходу кільця)
#define R_START     0x0
#define R_CW_FINAL  0x1
#define R_CW_BEGIN  0x2
#define R_CW_NEXT   0x3
#define R_CCW_BEGIN 0x4
#define R_CCW_FINAL 0x5
#define R_CCW_NEXT  0x6

// повнокрокова таблиця: рядок = стан, стовпець = зчитане (CLK<<1)|DT ∈ {0,1,2,3}
const uint8_t ttable[7][4] = {
  // R_START:      00           01           10           11
  {R_START,     R_CW_BEGIN,  R_CCW_BEGIN, R_START},
  // R_CW_FINAL
  {R_CW_NEXT,   R_START,     R_CW_FINAL,  R_START | DIR_CW},
  // R_CW_BEGIN
  {R_CW_NEXT,   R_CW_BEGIN,  R_START,     R_START},
  // R_CW_NEXT
  {R_CW_NEXT,   R_CW_BEGIN,  R_CW_FINAL,  R_START},
  // R_CCW_BEGIN
  {R_CCW_NEXT,  R_START,     R_CCW_BEGIN, R_START},
  // R_CCW_FINAL
  {R_CCW_NEXT,  R_CCW_FINAL, R_START,     R_START | DIR_CCW},
  // R_CCW_NEXT
  {R_CCW_NEXT,  R_CCW_FINAL, R_CCW_BEGIN, R_START},
};
