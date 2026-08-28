// Прикидка вихідної частоти каскаду декад у прошивці-помічнику
#include <stdint.h>
#include <stdio.h>

int main(void) {
    double f_clk = 32768.0;          // вхідний такт, Гц (годинниковий кварц)
    int stages   = 3;                // скільки декад у каскаді (кожна ділить на 10)
    double f_out = f_clk;
    for (int i = 0; i < stages; i++)
        f_out /= 10.0;               // кожен CO → CLK наступного = ще одне ÷10
    printf("після %d декад: %.4f Hz\n", stages, f_out);  // 32.7680 Hz
    return 0;
}
