#include "can_link.hpp"

#include <cerrno>
#include <cmath>
#include <cstring>
#include <stdexcept>
#include <system_error>

#include <net/if.h>
#include <poll.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <unistd.h>

#include <linux/can.h>
#include <linux/can/raw.h>

namespace carrier {
namespace {

constexpr std::uint32_t kStatusId = 0x100;
constexpr std::uint8_t kStatusFormat = 0x01;

}  // namespace

CanLink::CanLink(std::string_view ifname)
	: ifname_{ifname},
	  fd_{::socket(PF_CAN, SOCK_RAW | SOCK_CLOEXEC, CAN_RAW)}
{
	if (!fd_)
		throw std::system_error{errno, std::generic_category(),
					"socket(PF_CAN)"};

	::ifreq ifr{};
	std::strncpy(ifr.ifr_name, ifname_.c_str(), IFNAMSIZ - 1);

	// Інтерфейс існує лише після probe драйвера на вузлі can@0
	// і команди ip link set can0 up.
	if (::ioctl(fd_.get(), SIOCGIFINDEX, &ifr) < 0)
		throw std::system_error{errno, std::generic_category(),
					"нема інтерфейсу " + ifname_};

	const int enable = 1;
	if (::setsockopt(fd_.get(), SOL_CAN_RAW, CAN_RAW_FD_FRAMES,
			 &enable, sizeof enable) < 0)
		throw std::system_error{errno, std::generic_category(),
					ifname_ + " піднято без режиму fd"};

	::sockaddr_can addr{};
	addr.can_family = AF_CAN;
	addr.can_ifindex = ifr.ifr_ifindex;
	if (::bind(fd_.get(), reinterpret_cast<::sockaddr*>(&addr), sizeof addr) < 0)
		throw std::system_error{errno, std::generic_category(),
					"bind на " + ifname_};
}

void CanLink::send_status(double celsius, bool fault)
{
	::canfd_frame frame{};
	frame.can_id = kStatusId;
	frame.len = 8;
	frame.flags = CANFD_BRS;

	// У шину йде ціле в десятих градуса, а не double.
	const auto deci = static_cast<std::int16_t>(std::lround(celsius * 10.0));

	frame.data[0] = kStatusFormat;
	frame.data[1] = static_cast<std::uint8_t>(deci & 0xff);
	frame.data[2] = static_cast<std::uint8_t>((deci >> 8) & 0xff);
	frame.data[3] = fault ? 1 : 0;
	frame.data[4] = sequence_++;

	const ssize_t written = ::write(fd_.get(), &frame, sizeof frame);
	if (written < 0)
		throw std::system_error{errno, std::generic_category(),
					"передавання в " + ifname_};
	if (written != static_cast<ssize_t>(sizeof frame))
		throw std::runtime_error{"кадр пішов у " + ifname_ + " не повністю"};
}

std::optional<CanFrame> CanLink::receive(std::chrono::milliseconds timeout)
{
	::pollfd pfd{fd_.get(), POLLIN, 0};

	const int ready = ::poll(&pfd, 1, static_cast<int>(timeout.count()));
	if (ready < 0) {
		if (errno == EINTR)
			return std::nullopt;	// прийшов сигнал зупинки
		throw std::system_error{errno, std::generic_category(), "poll на " + ifname_};
	}
	if (ready == 0)
		return std::nullopt;

	::canfd_frame frame{};
	const ssize_t got = ::read(fd_.get(), &frame, sizeof frame);
	if (got < 0)
		throw std::system_error{errno, std::generic_category(),
					"читання з " + ifname_};

	// Класичний кадр приходить розміром CAN_MTU, кадр CAN-FD — CANFD_MTU:
	// структури збігаються початком, і розмір читання — єдина ознака.
	if (got != static_cast<ssize_t>(CAN_MTU) && got != static_cast<ssize_t>(CANFD_MTU))
		throw std::runtime_error{"обрізаний кадр з " + ifname_};

	CanFrame out;
	out.flexible_data = (got == static_cast<ssize_t>(CANFD_MTU));
	out.error_frame = (frame.can_id & CAN_ERR_FLAG) != 0;
	out.id = out.error_frame ? (frame.can_id & CAN_ERR_MASK)
				 : (frame.can_id & CAN_SFF_MASK);
	out.data.assign(frame.data, frame.data + frame.len);
	return out;
}

}  // namespace carrier
