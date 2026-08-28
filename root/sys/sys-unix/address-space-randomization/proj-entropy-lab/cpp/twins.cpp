/* twins.cpp — на чому ядро тягне жереб: на fork чи на execve?
 *   g++ -O2 -Wall -Wextra -fPIE -pie -o twins twins.cpp
 */
#include <iostream>
#include <iomanip>
#include <string_view>
#include <cstdint>
#include <sys/auxv.h>
#include <sys/wait.h>
#include <unistd.h>

static void say(std::string_view who)
{
	volatile char anchor = 0;
	std::cout << std::left << std::setw(12) << who << std::right << std::hex
	          << " entry=0x" << getauxval(AT_ENTRY)
	          << "  stack=0x" << reinterpret_cast<std::uintptr_t>(&anchor)
	          << "  vdso=0x" << getauxval(AT_SYSINFO_EHDR)
	          << std::dec << std::endl;
}

int main(int argc, char **argv)
{
	if (argc > 1 && std::string_view(argv[1]) == "exec") {
		say("після exec");
		return 0;
	}

	say("батько");

	pid_t pid = fork();
	if (pid == 0) {
		say("дитина fork");
		execl("/proc/self/exe", argv[0], "exec", static_cast<char *>(nullptr));
		perror("execl");
		_exit(127);
	}
	wait(nullptr);
	return 0;
}
