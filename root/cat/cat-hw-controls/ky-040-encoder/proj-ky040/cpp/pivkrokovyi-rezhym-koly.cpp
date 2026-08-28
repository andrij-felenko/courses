// Півкрокові стани
#define R_START      0x0
#define R_CCW_BEGIN  0x1
#define R_CW_BEGIN   0x2
#define R_START_M    0x3
#define R_CW_BEGIN_M 0x4
#define R_CCW_BEGIN_M 0x5

const uint8_t ttable_half[6][4] = {
  // R_START
  {R_START_M,           R_CW_BEGIN,    R_CCW_BEGIN,   R_START},
  // R_CCW_BEGIN
  {R_START_M | DIR_CCW, R_START,       R_CCW_BEGIN,   R_START},
  // R_CW_BEGIN
  {R_START_M | DIR_CW,  R_CW_BEGIN,    R_START,       R_START},
  // R_START_M (проміжний «спокій» усередині циклу)
  {R_START_M,           R_CCW_BEGIN_M, R_CW_BEGIN_M,  R_START},
  // R_CW_BEGIN_M
  {R_START_M,           R_START_M,     R_CW_BEGIN_M,  R_START | DIR_CW},
  // R_CCW_BEGIN_M
  {R_START_M,           R_CCW_BEGIN_M, R_START_M,     R_START | DIR_CCW},
};
