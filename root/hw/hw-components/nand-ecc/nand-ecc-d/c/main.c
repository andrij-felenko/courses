#include <stdint.h>
#include <stdio.h>

// Гаммінг(7,4): позиції 1..7, перевірні на 1,2,4 (степені двійки),
// дані d0..d3 на позиціях 3,5,6,7. Парність підмножини має бути 0.
static uint8_t encode(uint8_t data4) {
    uint8_t d0=(data4>>0)&1, d1=(data4>>1)&1, d2=(data4>>2)&1, d3=(data4>>3)&1;
    uint8_t bit[8] = {0};              // bit[1..7] — позиції коду
    bit[3]=d0; bit[5]=d1; bit[6]=d2; bit[7]=d3;
    bit[1]= bit[3]^bit[5]^bit[7];      // накриває позиції з розрядом 1
    bit[2]= bit[3]^bit[6]^bit[7];      // ...з розрядом 2
    bit[4]= bit[5]^bit[6]^bit[7];      // ...з розрядом 4
    uint8_t code=0;
    for (int i=1;i<=7;i++) code |= bit[i]<<(i-1);
    return code;                       // 7 бітів у молодших розрядах
}

// Повертає виправлений код; синдром = номер зіпсованої позиції (0 = чисто).
static uint8_t correct(uint8_t code, int *syndrome_out) {
    uint8_t b[8]={0};
    for (int i=1;i<=7;i++) b[i]=(code>>(i-1))&1;
    int s = 0;
    s |= (b[1]^b[3]^b[5]^b[7]) << 0;   // перерахунок парності підмножини 1
    s |= (b[2]^b[3]^b[6]^b[7]) << 1;   // ...підмножини 2
    s |= (b[4]^b[5]^b[6]^b[7]) << 2;   // ...підмножини 4
    if (s) code ^= (1u << (s-1));      // s — це і є номер біта; перевертаємо
    *syndrome_out = s;
    return code;
}

int main(void) {
    uint8_t code = encode(0b1011);           // закодували дані 1011
    uint8_t stored = code ^ (1u << 4);       // «флеш» перекинула біт на позиції 5
    int s; uint8_t fixed = correct(stored, &s);
    printf("синдром = %d -> позиція помилки; збіг із оригіналом: %s\n",
           s, fixed==code ? "так" : "ні");
    return 0;                                 // друкує: синдром = 5 ... так
}
