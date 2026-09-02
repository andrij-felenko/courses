#pragma once

#include <chrono>
#include <cstdint>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

#include "unique_fd.hpp"

namespace carrier {

struct CanFrame {
	std::uint32_t id{};
	std::vector<std::uint8_t> data;
	bool flexible_data{};	// кадр CAN-FD, а не класичний
	bool error_frame{};	// повідомлення від контролера, а не від вузла
};

// Сокет SocketCAN до інтерфейсу, що його підняв драйвер MCP2518FD.
class CanLink {
public:
	explicit CanLink(std::string_view ifname);

	CanLink(const CanLink&) = delete;
	CanLink& operator=(const CanLink&) = delete;

	void send_status(double celsius, bool fault);
	[[nodiscard]] std::optional<CanFrame> receive(std::chrono::milliseconds timeout);

	[[nodiscard]] const std::string& interface() const noexcept { return ifname_; }

private:
	std::string ifname_;
	UniqueFd fd_;
	std::uint8_t sequence_{};
};

}  // namespace carrier
