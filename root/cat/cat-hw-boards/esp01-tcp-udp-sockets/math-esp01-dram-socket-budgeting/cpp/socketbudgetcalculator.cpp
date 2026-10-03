#include <cstddef>

class SocketBudgetCalculator {
public:
    static constexpr std::size_t S_TCP_PCB = 160;
    static constexpr std::size_t S_HDR = 56;
    static constexpr std::size_t M_RESERVE = 8192;

    static std::size_t calculateTcpSocketMem(std::size_t tcpWnd, std::size_t mss) noexcept {
        std::size_t nPbuf = (tcpWnd + mss - 1) / mss;
        return S_TCP_PCB + tcpWnd + nPbuf * S_HDR;
    }

    static bool canOpenTcpSocket(std::size_t freeHeap, std::size_t tcpWnd, std::size_t mss) noexcept {
        std::size_t requiredMem = calculateTcpSocketMem(tcpWnd, mss);
        if (freeHeap < M_RESERVE) {
            return false;
        }
        return (freeHeap - M_RESERVE) >= requiredMem;
    }
};
