/* Запуск OpenOCD як дочірнього процесу з наглядом за часом виконання. */
#include "flash.h"

#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

#define OPENOCD_MAX_CMDS   6u
#define PROGRAM_TIMEOUT_MS 120000u
#define ERASE_TIMEOUT_MS   60000u
#define GRACE_MS           2000u

static rack_status_t wait_openocd(pid_t pid, unsigned timeout_ms)
{
    uint64_t deadline = rack_now_ms() + timeout_ms;
    bool asked_to_stop = false;
    bool killed = false;

    for (;;) {
        int status = 0;
        pid_t r = waitpid(pid, &status, WNOHANG);

        if (r == pid) {
            if (WIFEXITED(status)) {
                int code = WEXITSTATUS(status);
                if (code == 0) {
                    return RACK_OK;
                }
                fprintf(stderr, "openocd завершився з кодом %d\n", code);
                return RACK_FAIL;
            }
            fprintf(stderr, "openocd убито сигналом %d\n", WIFSIGNALED(status) ? WTERMSIG(status) : 0);
            return RACK_FAIL;
        }
        if (r < 0) {
            if (errno == EINTR) {
                continue;
            }
            fprintf(stderr, "waitpid(openocd): %s\n", strerror(errno));
            return RACK_FAIL;
        }

        if (rack_now_ms() >= deadline || rack_stop) {
            if (!asked_to_stop) {
                /* Найчастіша причина зависання — мертвий SWD: адаптер чекає на
                   відповідь ядра, якого вже немає. Спершу просимо піти по-доброму. */
                fprintf(stderr, "openocd не вкладається в час — SIGTERM\n");
                kill(pid, SIGTERM);
                asked_to_stop = true;
                deadline = rack_now_ms() + GRACE_MS;
            } else if (!killed) {
                kill(pid, SIGKILL);
                killed = true;
                deadline = rack_now_ms() + GRACE_MS;
            }
            /* Після SIGKILL лишається тільки прибрати зомбі — цикл це й робить. */
        }
        rack_sleep_ms(50);
    }
}

static rack_status_t run_openocd(int slot_id, const char *const cmds[], size_t ncmds,
                                 unsigned timeout_ms)
{
    if (ncmds == 0 || ncmds > OPENOCD_MAX_CMDS) {
        fprintf(stderr, "run_openocd: %zu команд — так не буває\n", ncmds);
        return RACK_FAIL;
    }

    /* Налагоджувачі стійки мають серійні номери DUT01…DUTnn; за тим самим номером
       udev будує /dev/dut-slot-XX-swd, тож демон і openocd говорять про один адаптер. */
    char serial[64];
    snprintf(serial, sizeof serial, "adapter serial DUT%02d", slot_id);

    char *argv[9 + 2 * OPENOCD_MAX_CMDS];
    size_t n = 0;
    argv[n++] = (char *)"openocd";
    argv[n++] = (char *)"-f";
    argv[n++] = (char *)"interface/cmsis-dap.cfg";
    argv[n++] = (char *)"-c";
    argv[n++] = serial;
    argv[n++] = (char *)"-f";
    argv[n++] = (char *)"target/stm32f4x.cfg";
    for (size_t i = 0; i < ncmds; i++) {
        argv[n++] = (char *)"-c";
        argv[n++] = (char *)cmds[i];
    }
    argv[n] = NULL;

    pid_t pid = fork();
    if (pid < 0) {
        fprintf(stderr, "fork: %s\n", strerror(errno));
        return RACK_FAIL;
    }

    if (pid == 0) {
        /* Наш stdout — це живий потік консолі плати, який читає CI. Балаканину
           openocd зводимо в stderr, щоб вона не змішалася з логом завантаження. */
        if (dup2(STDERR_FILENO, STDOUT_FILENO) < 0) {
            _exit(126);
        }
        int devnull = open("/dev/null", O_RDONLY | O_CLOEXEC);
        if (devnull >= 0) {
            dup2(devnull, STDIN_FILENO);
            close(devnull);
        }
        execvp("openocd", argv);
        fprintf(stderr, "не запускається openocd: %s\n", strerror(errno));
        _exit(127);
    }

    return wait_openocd(pid, timeout_ms);
}

rack_status_t rack_flash_program(int slot_id, const char *image_path)
{
    /* Шлях загортаємо у фігурні дужки Tcl: інакше пробіл у назві образу
       розлетівся б на два аргументи команди program. */
    char cmd[512];
    int len = snprintf(cmd, sizeof cmd, "program {%s} verify reset exit", image_path);
    if (len < 0 || (size_t)len >= sizeof cmd) {
        fprintf(stderr, "задовгий шлях до образу\n");
        return RACK_FAIL;
    }

    const char *cmds[] = { "init", "reset halt", cmd };
    return run_openocd(slot_id, cmds, sizeof cmds / sizeof cmds[0], PROGRAM_TIMEOUT_MS);
}

rack_status_t rack_flash_mass_erase(int slot_id)
{
    const char *erase[] = { "init", "reset halt", "stm32f4x mass_erase 0", "shutdown" };
    if (run_openocd(slot_id, erase, sizeof erase / sizeof erase[0], ERASE_TIMEOUT_MS) == RACK_OK) {
        return RACK_OK;
    }

    /* Стирання не пройшло — найімовірніше стоїть захист читання RDP Level 1:
       у цьому стані flash недоступна взагалі. Зняття захисту саме по собі
       стирає кристал повністю, тож другої спроби mass_erase не треба. */
    fprintf(stderr, "слот %02d: mass_erase не пройшов, пробую зняти RDP\n", slot_id);
    const char *unlock[] = { "init", "stm32f4x unlock 0", "shutdown" };
    return run_openocd(slot_id, unlock, sizeof unlock / sizeof unlock[0], ERASE_TIMEOUT_MS);
}
