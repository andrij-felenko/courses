#include <unistd.h>
#include <sys/reboot.h>

int main() {
    // В ідеальному світі це єдине, що робить система наприкінці
    // Для виклику потрібні root-права (CAP_SYS_BOOT)
    sync(); // Скинути кеші
    reboot(RB_POWER_OFF); // Апаратне вимкнення
    return 0; // Сюди виконання ніколи не дійде
}
