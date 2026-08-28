/* 
 * 1. fentry: Назва функції у SEC та макросі має точно відповідати BTF vmlinux.h.
 * Аргументи (dfd, filename, flags, mode) розпаковуються автоматично з ctx[0..3].
 */
SEC("fentry/do_sys_open")
int BPF_PROG(trace_do_sys_open, int dfd, const char *filename, int flags, umode_t mode)
{
    /* Аргументи доступні безпосередньо як C-змінні */
    return 0;
}

/* 
 * 2. fexit: Останнім аргументом у списку BPF_PROG ОБОВ'ЯЗКОВО додається ret / retval.
 * Він розпаковується з елемента ctx[n], де n — кількість вхідних аргументів.
 */
SEC("fexit/do_sys_open")
int BPF_PROG(trace_do_sys_open_exit, int dfd, const char *filename, int flags, umode_t mode, int ret)
{
    if (ret < 0) {
        /* Обробка помилки системного виклику (код повернення ret < 0) */
    }
    return 0;
}

/* 
 * 3. fmod_ret: Дозволяє змінити результат повернення функції ядра.
 * Якщо BPF-програма повертає ненульове значення (наприклад, -EPERM), 
 * BPF Trampoline пропускає виконання оригінальної функції ядра і повертає це значення.
 */
SEC("fmod_ret/security_file_open")
int BPF_PROG(prevent_file_open, struct file *file, int ret)
{
    /* Заборона відкриття файла: повертаємо -EPERM (-13) */
    return -13; 
}
