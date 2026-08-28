/* Взаємодія з буфером libhistory мовою C */
#include <stdio.h>
#include <readline/history.h>

void record_command(const char *cmd_text) {
    using_history();
    /* Додавання рядка до кільцевого масиву пам'яті */
    add_history(cmd_text);
    
    /* Збереження вмісту пам'яті у постійний файл */
    if (write_history("/home/user/.bash_history") != 0) {
        perror("write_history failed");
    }
}
