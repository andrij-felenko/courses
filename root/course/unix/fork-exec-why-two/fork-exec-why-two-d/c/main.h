pid_t pid = fork();
if (pid > 0) exit(0); /* перший батько виходить */

setsid(); /* створюється новий сеанс без керуючого термінала */

pid = fork();
if (pid > 0) exit(0); /* лідер сеансу виходить */

/* Онук більше ніколи не зможе випадково захопити термінал через open() */
chdir("/");
umask(0);
close(0); close(1); close(2);
open("/dev/null", O_RDWR); /* fd 0 */
dup2(0, 1);                /* fd 1 */
dup2(0, 2);                /* fd 2 */
execve("/usr/sbin/daemon", argv, envp);
