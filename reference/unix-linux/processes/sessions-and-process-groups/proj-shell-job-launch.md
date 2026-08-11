# ⚙️ Мінімальна оболонка, що правильно запускає завдання

Ось повна оболонка на C, яка вміє небагато — запустити конвеєр окремим завданням, віддати йому термінал, пережити `Ctrl+Z` і повернути зупинене завдання через `fg` чи `bg`, — зате робить це точно так, як `bash`. Керування завданнями зводиться до чотирьох викликів, і майже всі поломки саморобних оболонок — це три забуті дрібниці біля цих чотирьох.

## Умова

Програма зветься `mysh`, читає рядок, розділяє його по `|` і запускає ланки одним завданням:

```
mysh$ find / -name core | grep -v proc | less
```

Вимоги — рівно ті, за якими впізнають робочу оболонку:

- `Ctrl+C` убиває завдання, а не оболонку; `Ctrl+Z` зупиняє завдання й повертає промпт;
- `fg` продовжує зупинене завдання разом із терміналом, `bg` — без термінала;
- `less` після `fg` малює екран так, наче його не чіпали, — отже, режим термінала теж повертається;
- запущені програми не перероблено: працюють справжні `/usr/bin/find` і `/usr/bin/less`, які про наше завдання нічого не знають.

Двох речей тут навмисно немає. Розбір рядка примітивний — ані лапок, ані підставлянь ([розкриття й лапки в оболонці](book:unix-linux/expansion-and-quoting)); і бухгалтерія `close` у конвеєрі не переказується, вона розібрана окремо ([конвеєр власними руками](book:unix-linux/pipe-and-fifo/proj-pipeline-by-hand.md)). Тут цікаве інше.

## Ідея: одна операція, за яку карають

Термінал зберігає одне число — номер групи переднього плану. Усе керування завданнями — це питання, хто й коли це число переставляє. За життя одного завдання оболонка переставляє його чотири рази: віддала при запуску, забрала на `Ctrl+Z`, віддала знову на `fg`, забрала, коли завдання вийшло.

![Смуга власності термінала й дві доріжки — оболонки й завдання — з чотирма моментами передавання](/reference/unix-linux/processes/sessions-and-process-groups/img/terminal-handover.svg)

*Оболонка тримає термінал лише поки друкує промпт: половину часу вона фонова, і саме з фону мусить забирати термінал назад.*

Складність не в передаваннях, а в охороні. Процес фонової групи, який чіпає **налаштування** термінала — `tcsetattr`, `tcsetpgrp`, — дістає `SIGTTOU`, і типова дія цього сигналу — зупинення. А оболонка забирає термінал саме тоді, коли вона фонова: доки завдання працює, покажчик переднього плану вказує на нього, а не на неї.

Звідси спокуслива й хибна думка: «отже, боронитися треба лише на поверненні». Коли оболонка **віддає** термінал, вона ще передня, і `tcsetpgrp` проходить безкарно — але щойно цей виклик повернувся, вона вже фонова, і наступний рядок тієї самої функції, `tcsetattr` із режимом термінала для завдання, уже карається. Тому `SIGTTOU` блокують на все передавання, в обидва боки.

Блокування тут не хитрість. POSIX описує його як передбачену поведінку: якщо той, хто викликає, блокує або нехтує `SIGTTOU`, операція просто виконується й жодного сигналу не надсилають — так сказано і про `tcsetpgrp`, і про `tcsetattr` ([диспозиція сигналу](book:unix-linux/signal-disposition) — три можливі долі сигналу: типова дія, нехтування, власний обробник).

> 🔧 **Навіщо це.** Оболонка, що забирає термінал наївно, не падає й не друкує помилки — вона тихо переходить у стан `T` і завмирає з порожнім екраном. Клавіатура при цьому теж мертва: покажчик переднього плану вказує на групу, у якій уже нікого немає, тож `Ctrl+C` нікому не адресовано. Симптом «термінал завис і не їсть процесора» майже завжди означає саме це, і перевіряється він одним поглядом на стовпчик `STAT` у `ps` із сусіднього вікна.

## Код

Стан оболонки — це збережений режим термінала й одне завдання. Списку завдань тут немає свідомо: другий і третій запис нічого не додають до механіки.

```c
#define _GNU_SOURCE
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <termios.h>
#include <unistd.h>

#define MAXP 8

struct job {
    pid_t pgid;                 /* імʼя групи = номер першої ланки */
    int   n;
    pid_t pid[MAXP];
    char  st[MAXP];             /* 'r' — живий · 's' — зупинений · 'x' — помер */
    struct termios tmodes;      /* режим термінала, знятий у мить зупинення */
    char  cmd[128];
};

static int   tty;               /* дескриптор керуючого термінала */
static pid_t shell_pgid;
static struct termios shell_tmodes;
```

Обидва передавання термінала — окремі функції, і кожна починається з блокування `SIGTTOU`:

```c
/* Віддати термінал групі pgid і, якщо треба, поставити її режим термінала.
   Блокуємо на ВЕСЬ виклик: щойно tcsetpgrp переведе покажчик на іншу групу,
   ми вже фонові — і наступний же tcsetattr зупинив би нас самих. */
static void give_terminal(pid_t pgid, const struct termios *modes)
{
    sigset_t block, old;
    sigemptyset(&block);
    sigaddset(&block, SIGTTOU);
    sigprocmask(SIG_BLOCK, &block, &old);

    if (tcsetpgrp(tty, pgid) < 0)
        perror("tcsetpgrp");
    if (modes)
        tcsetattr(tty, TCSADRAIN, modes);

    sigprocmask(SIG_SETMASK, &old, NULL);
}

/* Забрати термінал собі. Тут оболонка фонова ВЖЕ на першому рядку. */
static void take_terminal(struct job *j, int save_modes)
{
    sigset_t block, old;
    sigemptyset(&block);
    sigaddset(&block, SIGTTOU);
    sigprocmask(SIG_BLOCK, &block, &old);

    if (save_modes)
        tcgetattr(tty, &j->tmodes);       /* завдання ще житиме — зберігаємо його режим */
    tcsetpgrp(tty, shell_pgid);
    tcsetattr(tty, TCSADRAIN, &shell_tmodes);

    sigprocmask(SIG_SETMASK, &old, NULL);
}
```

Пробудження оболонки складається з двох частин, і порядок між ними важить:

```c
static void shell_init(void)
{
    tty = STDIN_FILENO;
    if (!isatty(tty)) {
        fputs("mysh: вхід — не термінал\n", stderr);
        exit(1);
    }

    /* Нас могли запустити у фоні. Доки термінал не наш, зупиняємо себе самі —
       і цей цикл мусить стояти ДО того, як ми почнемо нехтувати SIGTTIN,
       інакше він крутитиметься вічно. */
    while (tcgetpgrp(tty) != (shell_pgid = getpgrp()))
        kill(-shell_pgid, SIGTTIN);

    signal(SIGINT,  SIG_IGN);   /* Ctrl+C на промпті не має вбивати оболонку */
    signal(SIGQUIT, SIG_IGN);
    signal(SIGTSTP, SIG_IGN);   /* і Ctrl+Z не має її зупиняти */
    signal(SIGTTIN, SIG_IGN);

    shell_pgid = getpid();
    setpgid(shell_pgid, shell_pgid);   /* оболонка — сама собі завдання */
    give_terminal(shell_pgid, NULL);   /* після setpgid ми вже фонові: блокування потрібне */
    tcgetattr(tty, &shell_tmodes);     /* еталон, до якого повертатимемо термінал */
}
```

Дитина між `fork` і `exec` робить три речі, і жодну з них не можна перекласти на батька:

```c
static void child_prepare(pid_t pgid)
{
    setpgid(0, pgid);           /* pgid == 0 → «стань лідером власної групи» */

    /* Знехтуваний сигнал ЛИШАЄТЬСЯ знехтуваним після exec. Не скинемо —
       і запущена програма не відреагує ні на Ctrl+C, ні на Ctrl+Z. */
    signal(SIGINT,  SIG_DFL);
    signal(SIGQUIT, SIG_DFL);
    signal(SIGTSTP, SIG_DFL);
    signal(SIGTTIN, SIG_DFL);
    signal(SIGTTOU, SIG_DFL);

    sigset_t empty;             /* маска теж переживає exec */
    sigemptyset(&empty);
    sigprocmask(SIG_SETMASK, &empty, NULL);
}
```

Чекання винесене окремо, бо вся його суть — в одному прапорці:

```c
static int job_stopped(const struct job *j)
{
    for (int i = 0; i < j->n; i++)
        if (j->st[i] == 's')
            return 1;
    return 0;
}

/* Чекаємо, доки в завданні лишиться бодай один живий процес.
   WUNTRACED — це «повідом і про зупинення, не тільки про смерть».
   Без нього waitpid просто спатиме далі, а завдання вже нікуди не рухається. */
static int wait_job(struct job *j)
{
    for (;;) {
        int running = 0;
        for (int i = 0; i < j->n; i++)
            if (j->st[i] == 'r')
                running++;
        if (running == 0)
            break;

        int status;
        pid_t p = waitpid(-j->pgid, &status, WUNTRACED);
        if (p < 0) {
            if (errno == EINTR)
                continue;
            break;                        /* ECHILD: забирати вже нікого */
        }
        for (int i = 0; i < j->n; i++)
            if (j->pid[i] == p)
                j->st[i] = WIFSTOPPED(status) ? 's' : 'x';
    }
    return job_stopped(j);
}
```

Запуск завдання. Групу створюють двічі — і в дитині, і в батькові:

```c
static void launch_job(struct job *j, char **cmd[], int n, int foreground)
{
    int in = STDIN_FILENO;

    for (int i = 0; i < n; i++) {
        int pfd[2] = { -1, -1 };
        if (i + 1 < n && pipe(pfd) < 0) { perror("pipe"); return; }

        pid_t pid = fork();
        if (pid == 0) {
            child_prepare(j->pgid);
            if (in != STDIN_FILENO)  { dup2(in, STDIN_FILENO);      close(in);     }
            if (pfd[1] >= 0)         { dup2(pfd[1], STDOUT_FILENO); close(pfd[1]); }
            if (pfd[0] >= 0)           close(pfd[0]);
            execvp(cmd[i][0], cmd[i]);
            dprintf(STDERR_FILENO, "mysh: %s: %s\n", cmd[i][0], strerror(errno));
            _exit(127);
        }
        if (pid < 0) { perror("fork"); return; }

        if (j->pgid == 0)
            j->pgid = pid;      /* перша ланка дає групі імʼя */
        setpgid(pid, j->pgid);  /* те саме ВДРУГЕ, з боку батька; помилку ігноруємо свідомо */
        j->pid[j->n] = pid;
        j->st[j->n++] = 'r';

        if (in != STDIN_FILENO) close(in);
        if (pfd[1] >= 0)        close(pfd[1]);
        in = pfd[0];
    }

    if (!foreground) {
        printf("[1] %d\n", (int)j->pgid);
        return;
    }

    give_terminal(j->pgid, NULL);          /* режиму термінала в завдання ще немає */
    int stopped = wait_job(j);
    take_terminal(j, stopped);
    if (stopped)
        printf("\n[1]+ Зупинено   %s\n", j->cmd);
}
```

Відновлення — дві короткі функції, у яких видно всю різницю між `fg` і `bg`:

```c
static void do_fg(struct job *j)
{
    for (int i = 0; i < j->n; i++)
        if (j->st[i] == 's') j->st[i] = 'r';

    give_terminal(j->pgid, &j->tmodes);    /* спершу режим термінала, який був до Ctrl+Z */
    kill(-j->pgid, SIGCONT);               /* і аж тоді будимо — ВСЮ групу, не лідера */
    take_terminal(j, wait_job(j));
}

static void do_bg(struct job *j)
{
    for (int i = 0; i < j->n; i++)
        if (j->st[i] == 's') j->st[i] = 'r';

    kill(-j->pgid, SIGCONT);               /* термінала не даємо — хай працює у фоні */
    printf("[1]+ %s &\n", j->cmd);
}
```

Головний цикл нецікавий рівно настільки, наскільки цікаве все попереднє:

```c
int main(void)
{
    char line[512], shown[512];
    static char *slot[MAXP][16];
    struct job cur;
    memset(&cur, 0, sizeof cur);

    shell_init();
    for (;;) {
        printf("mysh$ ");
        fflush(stdout);
        if (!fgets(line, sizeof line, stdin)) break;
        line[strcspn(line, "\n")] = '\0';
        if (!*line)              continue;
        if (!strcmp(line, "exit")) break;
        if (!strcmp(line, "fg")) { if (job_stopped(&cur)) do_fg(&cur); continue; }
        if (!strcmp(line, "bg")) { if (job_stopped(&cur)) do_bg(&cur); continue; }

        snprintf(shown, sizeof shown, "%s", line);
        int background = 0;
        size_t len = strlen(line);
        if (len && line[len - 1] == '&') { background = 1; line[len - 1] = '\0'; }

        char *part[MAXP];
        int n = 0;
        for (char *s = strtok(line, "|"); s && n < MAXP; s = strtok(NULL, "|"))
            part[n++] = s;

        char **argvv[MAXP];
        for (int i = 0; i < n; i++) {
            int k = 0;
            for (char *w = strtok(part[i], " \t"); w && k < 15; w = strtok(NULL, " \t"))
                slot[i][k++] = w;
            slot[i][k] = NULL;
            argvv[i] = slot[i];
        }
        if (n == 0 || argvv[0][0] == NULL) continue;

        memset(&cur, 0, sizeof cur);
        snprintf(cur.cmd, sizeof cur.cmd, "%s", shown);
        launch_job(&cur, argvv, n, !background);
    }
    return 0;
}
```

## Перевірка

```
$ cc -O2 -Wall -o mysh mysh.c
$ ./mysh
mysh$ find / -name core | grep -v proc | less
```

Натисніть `Ctrl+Z` — і подивіться з сусіднього вікна, що саме вийшло:

```
mysh$ 
[1]+ Зупинено   find / -name core | grep -v proc | less
mysh$
```

```
$ ps -o pid,pgid,tpgid,stat,cmd -t pts/5
  PID  PGID TPGID STAT CMD
 4210  4210  4210 S+   ./mysh
 4271  4271  4210 T    find / -name core
 4272  4271  4210 T    grep -v proc
 4273  4271  4210 T    less
```

Читається це так. Три ланки — одна група 4271, і всі три в стані `T`: `Ctrl+Z` дістав усіх, хоча оболонка надсилала сигнал одному номеру. `TPGID` знову 4210, тобто термінал повернувся до оболонки, і плюс у стовпчику `STAT` тепер у неї. `fg` поверне картинку `less` цілою, `bg` — випустить конвеєр працювати далі без клавіатури.

## Складність і пастки

**Забутий `SIGTTOU` зупиняє оболонку.** Приберіть `sigprocmask` із `take_terminal` — і після першого ж завершеного завдання оболонка сама себе зупинить на `tcsetpgrp`. Промпт не повернеться, `Ctrl+C` теж не допоможе: покажчик переднього плану вказує на групу, у якій уже нікого немає. Оживити можна лише ззовні — `kill -CONT` із сусіднього термінала, — і на наступному завданні все повториться.

**Забутий `WUNTRACED` робить зупинене завдання невидимим.** Без цього прапорця `waitpid` повідомляє лише про смерть, а зупинення для нього — не подія. Оболонка спатиме, завдання стоятиме в стані `T` і триматиме термінал, а виглядатиме це як «програма зависла». Прапорця тут вимагає сама конструкція: для того, хто керує завданнями, зупинення — така сама подія, як завершення ([завершення, wait і зомбі](book:unix-linux/exit-wait-zombies) — статус дитини живе в ядрі, доки батько його не забере; `WCONTINUED` — дзеркальний прапорець про продовження).

**Щілина між `fork` і `exec` закривається лише подвоєнням.** Обидва виклики `setpgid` потрібні, і помилку батьківського треба ігнорувати: `EACCES` означає, що дитина вже зробила `exec` (отже, групу вона поставила собі сама), `ESRCH` — що вона встигла вийти. Обидва — нормальний перебіг, а не збій. І `give_terminal` можна кликати лише після того, як батьківський `setpgid` повернувся: інакше групи з таким номером ще не існує, і `tcsetpgrp` відповість `EPERM`.

**Нехтування переживає `exec`.** Якщо в `child_prepare` не скинути диспозиції, знехтувані сигнали оболонки переїдуть у запущену програму, і жодна команда, запущена з вашої оболонки, не відреагує на `Ctrl+C` та `Ctrl+Z`. Симптом упізнаваний: у `bash` те саме працює, у вашій оболонці — ні. Маска сигналів переїжджає так само, тому в дитині її знімають окремим рядком ([exec: заміна образу](book:unix-linux/exec-semantics) — що саме переживає заміну коду).

**Режим термінала належить завданню, а не оболонці.** Не збережете `tmodes` у мить зупинення — `less` після `fg` прокинеться в канонічному режимі з відлунням: сама програма вважає, що термінал сирий, а він уже ні. Не повернете `shell_tmodes` собі — промпт лишиться без відлуння й без редагування рядка ([TTY і послідовний порт: модель termios](book:unix-linux/tty-and-termios) — набір прапорців, які визначають, чи перетворює драйвер натискання на сигнали і чи віддає рядок по символу).

**Про фонові завдання ця оболонка не дізнається сама.** Вона не чекає на них, тож вони лишаються зомбі, а їхні зупинення й смерті проходять повз неї. Справжня оболонка ловить `SIGCHLD`, збирає статуси через `waitpid(-1, …, WNOHANG | WUNTRACED)` і друкує сповіщення не в обробнику, а перед наступним промптом — бо `printf` в обробнику робити не можна ([що взагалі можна робити в обробнику сигналу](book:unix-linux/async-signal-safety) — перелік викликів, безпечних усередині асинхронного обробника). Звідти ж і звичка `bash` показувати «Завершено» із запізненням на один рядок.

І наостанок дрібниця, яка добре показує, що механізм працює рівно так, як описано: `Ctrl+Z` на промпті `mysh` не робить нічого. `SIGTSTP` іде групі переднього плану — а це наша оболонка, яка цей сигнал нехтує. Зупинити її з `bash` не вийде взагалі; справжні оболонки тримають для цього окрему вбудовану команду `suspend`, яка надсилає `SIGSTOP` самій собі — сигнал, якого не можна ані знехтувати, ані перехопити ([керування завданнями й термінальні сигнали](book:unix-linux/job-control) — домовленості, за якими оболонка розкладає команди по завданнях).
