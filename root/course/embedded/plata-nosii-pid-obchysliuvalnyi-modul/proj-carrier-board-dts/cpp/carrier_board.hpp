#pragma once

#include <chrono>
#include <cstddef>
#include <filesystem>
#include <optional>
#include <string>
#include <string_view>

#include <gpiod.hpp>

#include "unique_fd.hpp"

namespace carrier {

// Термодавач TMP102 через hwmon. Номер hwmonN залежить від порядку probe,
// тому теку шукаємо за іменем драйвера, а не зашиваємо hwmon0.
class Thermometer {
public:
	explicit Thermometer(std::string_view driver_name);

	[[nodiscard]] double celsius() const;
	[[nodiscard]] const std::filesystem::path& input_path() const noexcept
	{
		return input_;
	}

private:
	std::filesystem::path input_;
};

// Годинник PCF85063A: ядро віддає його як /dev/rtcN, читання — ioctl.
class RtcClock {
public:
	explicit RtcClock(std::filesystem::path device = "/dev/rtc0");

	[[nodiscard]] std::chrono::system_clock::time_point now() const;

private:
	std::filesystem::path device_;
	UniqueFd fd_;
};

// Табличка плати з EEPROM 24LC64 — драйвер at24 віддає її одним файлом.
[[nodiscard]] std::string read_board_id(const std::filesystem::path& eeprom,
					std::size_t length = 32);

// Аварійний світлодіод на лінії, навмисно не відданій gpio-leds.
// Час життя об'єкта і є час володіння лінією.
class FaultIndicator {
public:
	FaultIndicator(std::string_view chip_name, unsigned int offset);

	FaultIndicator(const FaultIndicator&) = delete;
	FaultIndicator& operator=(const FaultIndicator&) = delete;

	~FaultIndicator();

	void set(bool on);
	[[nodiscard]] bool state() const noexcept { return state_; }

	// Хто тримає лінію: ядро підписується назвою вузла з дерева пристроїв.
	// std::nullopt — лінія вільна, тобто вузол DTS не спрацював.
	[[nodiscard]] std::optional<std::string> consumer_of(unsigned int offset);

private:
	gpiod::chip chip_;
	gpiod::line line_;
	unsigned int offset_;
	bool state_{false};
};

[[nodiscard]] std::string format_utc(std::chrono::system_clock::time_point tp);

}  // namespace carrier
