/* twins.c — на чому ядро тягне жереб: на fork чи на execve?
 *   cc -O2 -Wall -Wextra -fPIE -pie -o twins twins.c
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <sys/auxv.h>
#include <sys/wait.h>
#include <unistd.h>

static void say(const char *who)
{
	volatile char anchor = 0;
	printf("%-12s entry=%#lx  stack=%#lx  vdso=%#lx\n", who,
	       getauxval(AT_ENTRY), (unsigned long) &anchor,
	       getauxval(AT_SYSINFO_EHDR));
	fflush(stdout);          /* щоб дитина не успадкувала непорожній буфер */
}

int main(int argc, char **argv)
{
	if (argc > 1 && strcmp(argv[1], "exec") == 0) {
		say("після exec");
		return 0;
	}

	say("батько");

	pid_t pid = fork();
	if (pid == 0) {
		say("дитина fork");
		execl("/proc/self/exe", argv[0], "exec", (char *) NULL);
		perror("execl");
		_exit(127);
	}
	wait(NULL);
	return 0;
}
