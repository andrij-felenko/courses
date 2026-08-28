/* utf8_demo.c — коректний вивід UTF-8 у консоль Windows мовою C */
#include <windows.h>
#include <stdio.h>

int main(void) {
    UINT old_cp = GetConsoleOutputCP();

    /* Встановлюємо активну сторінку виводу консолі в UTF-8 (65001) */
    SetConsoleOutputCP(CP_UTF8);

    /* Рядок скомпільовано з прапорцем /utf-8 */
    printf("Український текст: Вітання зі світу системної збірки!\n");
    printf("Спеціальні символи Unicode: ⚡ 🚀 🔧 [OK]\n");

    /* Відновлюємо початкову сторінку перед завершенням */
    SetConsoleOutputCP(old_cp);
    return 0;
}
