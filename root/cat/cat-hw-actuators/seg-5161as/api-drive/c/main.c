#include <stdint.h>

// Кожен сегмент — окремий біт у масці (порядок a..g, DP)
#define SA  (1 << 0)
#define SB  (1 << 1)
#define SC  (1 << 2)
#define SD  (1 << 3)
#define SE  (1 << 4)
#define SF  (1 << 5)
#define SG  (1 << 6)
#define SDP (1 << 7)

// Таблиця символів: 0..9, потім A b C d E F (для HEX).
// Маска зібрана з сегментів — видно, які риски світяться.
const uint8_t FONT[16] = {
  SA|SB|SC|SD|SE|SF,       // 0
        SB|SC,             // 1
  SA|SB|   SD|SE|   SG,    // 2
  SA|SB|SC|SD|      SG,    // 3
        SB|SC|   SF|SG,    // 4
  SA|   SC|SD|SF|SG,       // 5
  SA|   SC|SD|SE|SF|SG,    // 6
  SA|SB|SC,                // 7
  SA|SB|SC|SD|SE|SF|SG,    // 8
  SA|SB|SC|SD|   SF|SG,    // 9
  SA|SB|SC|   SE|SF|SG,    // A
        SC|SD|SE|SF|SG,    // b (мала, бо велика «B» = «8»)
  SA|      SD|SE|SF,       // C
     SB|SC|SD|SE|   SG,    // d (мала, бо велика «D» = «0»)
  SA|      SD|SE|SF|SG,    // E
  SA|         SE|SF|SG,    // F
};
