#pragma once

#include <string>

namespace tty {

// Розкладка struct termios на цій системі — зміщення й розміри полів —
// поруч із ядровою struct termios2 та звіркою двох ABI.
std::string abi_report();

}  // namespace tty
