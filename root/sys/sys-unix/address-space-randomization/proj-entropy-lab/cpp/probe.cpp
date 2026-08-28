/* probe.cpp — друкує один рядок орієнтирів адресного простору цього процесу.
 *
 *   g++ -O2 -Wall -Wextra -fPIE -pie -o probe probe.cpp -ldl
 */
#include <iostream>
#include <iomanip>
#include <string_view>
#include <cstdint>
#include <dlfcn.h>
#include <link.h>
#include <sys/auxv.h>
#include <sys/syscall.h>
#include <unistd.h>

int main(int argc, char **argv)
{
	// Межу купи знімаємо ПЕРШОЮ дією.
	const auto brk0 = static_cast<std::uintptr_t>(syscall(SYS_brk, 0));

	volatile char anchor = 0;
	const auto stack = reinterpret_cast<std::uintptr_t>(&anchor);

	const auto entry = getauxval(AT_ENTRY);
	const auto vdso  = getauxval(AT_SYSINFO_EHDR);
	const auto ldso  = getauxval(AT_BASE);

	std::uintptr_t sym = 0, base = 0;
	std::string_view path = "?";
	void *h = dlopen("libc.so.6", RTLD_LAZY | RTLD_NOLOAD);
	if (h != nullptr) {
		link_map *lm = nullptr;
		sym = reinterpret_cast<std::uintptr_t>(dlsym(h, "printf"));
		if (dlinfo(h, RTLD_DI_LINKMAP, &lm) == 0 && lm != nullptr) {
			base = static_cast<std::uintptr_t>(lm->l_addr);
			if (lm->l_name != nullptr && lm->l_name[0] != '\0') {
				path = lm->l_name;
			}
		}
	}

	if (argc > 1 && std::string_view(argv[1]) == "-v") {
		std::cerr << "відображений файл: " << path << "\nзсув printf у ньому: 0x"
		          << std::hex << (sym - base) << std::dec << '\n';
	}

	std::cout << std::hex
	          << "libc=0x" << base << " libcsym=0x" << sym
	          << " entry=0x" << entry << " stack=0x" << stack
	          << " brk=0x" << brk0 << " vdso=0x" << vdso
	          << " ldso=0x" << ldso << std::dec << '\n';
	return 0;
}
