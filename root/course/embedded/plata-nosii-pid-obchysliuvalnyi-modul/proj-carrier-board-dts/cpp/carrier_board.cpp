#include "carrier_board.hpp"

#include <cerrno>
#include <cstring>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <system_error>

#include <fcntl.h>
#include <sys/ioctl.h>

#include <linux/rtc.h>

namespace carrier {
namespace {

std::string read_first_line(const std::filesystem::path& path)
{
	std::ifstream in{path};
	if (!in)
		throw std::system_error{errno, std::generic_category(),
					"не відкрити " + path.string()};
	std::string line;
	std::getline(in, line);
	return line;
}

}  // namespace

Thermometer::Thermometer(std::string_view driver_name)
{
	const std::filesystem::path root{"/sys/class/hwmon"};
	std::error_code ec;

	for (const auto& entry : std::filesystem::directory_iterator{root, ec}) {
		const auto name_file = entry.path() / "name";
		if (!std::filesystem::exists(name_file))
			continue;
		if (read_first_line(name_file) != driver_name)
			continue;

		input_ = entry.path() / "temp1_input";
		return;
	}

	throw std::runtime_error{"драйвер " + std::string{driver_name} +
				 " не зареєстрував hwmon: перевірте sensor@48 у DTS"};
}

double Thermometer::celsius() const
{
	std::ifstream in{input_};
	if (!in)
		throw std::system_error{errno, std::generic_category(),
					"не відкрити " + input_.string()};

	long milli{};
	if (!(in >> milli))
		throw std::runtime_error{"неочікуваний вміст " + input_.string()};

	// hwmon міряє в тисячних градуса незалежно від давача.
	return static_cast<double>(milli) / 1000.0;
}

RtcClock::RtcClock(std::filesystem::path device)
	: device_{std::move(device)},
	  fd_{::open(device_.c_str(), O_RDONLY | O_CLOEXEC)}
{
	if (!fd_)
		throw std::system_error{errno, std::generic_category(),
					"не відкрити " + device_.string()};
}

std::chrono::system_clock::time_point RtcClock::now() const
{
	::rtc_time rt{};
	if (::ioctl(fd_.get(), RTC_RD_TIME, &rt) < 0)
		throw std::system_error{errno, std::generic_category(),
					"RTC_RD_TIME на " + device_.string()};

	std::tm tm{};
	tm.tm_sec = rt.tm_sec;
	tm.tm_min = rt.tm_min;
	tm.tm_hour = rt.tm_hour;
	tm.tm_mday = rt.tm_mday;
	tm.tm_mon = rt.tm_mon;
	tm.tm_year = rt.tm_year;
	tm.tm_isdst = -1;

	// Мікросхема тримає час в UTC — саме так його ставить hwclock у Linux.
	return std::chrono::system_clock::from_time_t(::timegm(&tm));
}

std::string read_board_id(const std::filesystem::path& eeprom, std::size_t length)
{
	std::ifstream in{eeprom, std::ios::binary};
	if (!in)
		throw std::system_error{errno, std::generic_category(),
					"не відкрити " + eeprom.string()};

	std::string raw(length, '\0');
	in.read(raw.data(), static_cast<std::streamsize>(length));
	raw.resize(static_cast<std::size_t>(in.gcount()));

	// Файл бінарний: на початку сторінки текстова табличка, далі сміття.
	for (char& c : raw) {
		const auto byte = static_cast<unsigned char>(c);
		if (byte < 0x20 || byte > 0x7e)
			c = '.';
	}
	return raw;
}

FaultIndicator::FaultIndicator(std::string_view chip_name, unsigned int offset)
	: chip_{std::string{chip_name}}, line_{chip_.get_line(offset)}, offset_{offset}
{
	// Якби GPIO26 описали в gpio-leds, лінію вже тримало б ядро,
	// і request кинув би -EBUSY. Скажемо це зрозуміло одразу.
	if (line_.is_used())
		throw std::runtime_error{"GPIO" + std::to_string(offset) +
					 " зайнято ядром (" + line_.consumer() +
					 "): приберіть вузол із gpio-leds"};

	line_.request({"carrier-monitor", gpiod::line_request::DIRECTION_OUTPUT, 0}, 0);
}

FaultIndicator::~FaultIndicator()
{
	// Ядро віддало б лінію й саме, коли закриється дескриптор, — але
	// світлодіод залишився б горіти. Деструктор гасить і не кидає.
	try {
		line_.set_value(0);
		line_.release();
	} catch (const std::exception&) {
	}
}

void FaultIndicator::set(bool on)
{
	if (on == state_)
		return;
	line_.set_value(on ? 1 : 0);
	state_ = on;
}

std::optional<std::string> FaultIndicator::consumer_of(unsigned int offset)
{
	auto line = chip_.get_line(offset);
	if (!line.is_used())
		return std::nullopt;
	return line.consumer();
}

std::string format_utc(std::chrono::system_clock::time_point tp)
{
	const std::time_t t = std::chrono::system_clock::to_time_t(tp);
	std::tm tm{};
	::gmtime_r(&t, &tm);

	std::ostringstream out;
	out << std::put_time(&tm, "%Y-%m-%d %H:%M:%S");
	return out.str();
}

}  // namespace carrier
