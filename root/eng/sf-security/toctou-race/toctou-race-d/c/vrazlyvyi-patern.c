#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

void process_user_report(const char* filepath, const char* data, size_t len) {
    // ВРАЗЛИВІСТЬ (TOC): перевіряємо права реального користувача
    if (access(filepath, W_OK) != 0) {
        perror("access denied");
        return;
    }

    // ВІКНО ГОНКИ (Δt): тут атакуючий підмінює filepath на симлінк!

    // ВРАЗЛИВІСТЬ (TOU): відкриття за шляхом розв'язує підсунутий симлінк
    int fd = open(filepath, O_WRONLY | O_TRUNC);
    if (fd >= 0) {
        write(fd, data, len);
        close(fd);
    }
}
