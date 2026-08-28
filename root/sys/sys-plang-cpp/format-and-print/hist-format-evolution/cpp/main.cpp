// C++98/C++03: Потоковий вивід через std::ostringstream
#include <iostream>
#include <sstream>
#include <iomanip>

std::string format_log_legacy(const std::string& host, int port) {
    std::ostringstream ss;
    ss << "Connecting to " << host << ":" << std::dec << port 
       << " (HEX: 0x" << std::hex << std::uppercase << std::setw(4) << std::setfill('0') << port << ")";
    return ss.str();
}
