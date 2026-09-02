// main.cpp — той самий монітор плати-носія, але власником кожного ресурсу
// є об'єкт: помилки летять винятками, лінії й сокет віддаються деструкторами.
#include <atomic>
#include <chrono>
#include <cstdlib>
#include <exception>
#include <iomanip>
#include <iostream>
#include <optional>
#include <thread>

#include <signal.h>

#include "can_link.hpp"
#include "carrier_board.hpp"

namespace {

constexpr std::string_view kHwmonDriver = "tmp102";
constexpr std::string_view kGpioChip = "gpiochip0";
constexpr unsigned int kFaultLed = 26;
constexpr unsigned int kHeartbeatLed = 16;
constexpr unsigned int kUserButton = 17;

// Дві межі, а не одна: рівно на 60 °C одна межа дала б миготіння.
constexpr double kTripOn = 60.0;
constexpr double kTripOff = 57.0;

std::atomic<bool> stop_requested{false};

extern "C" void on_signal(int) { stop_requested.store(true); }

void install_handlers()
{
	struct sigaction sa {};
	sa.sa_handler = on_signal;
	::sigaction(SIGINT, &sa, nullptr);
	::sigaction(SIGTERM, &sa, nullptr);
}

void idle_second()
{
	std::this_thread::sleep_for(std::chrono::seconds{1});
}

void print_claim(carrier::FaultIndicator& panel, unsigned int offset,
		 std::string_view expected)
{
	if (const auto who = panel.consumer_of(offset))
		std::cout << "GPIO" << offset << " тримає ядро (" << *who
			  << "), очікували " << expected << '\n';
	else
		std::cout << "GPIO" << offset << " вільна — вузол " << expected
			  << " у дереві не спрацював\n";
}

void print_frame(const carrier::CanFrame& frame)
{
	if (frame.error_frame) {
		std::cerr << "CAN: кадр помилки, прапорці 0x" << std::hex << frame.id
			  << std::dec << '\n';
		return;
	}

	std::cout << "CAN rx id=0x" << std::hex << frame.id << std::dec
		  << (frame.flexible_data ? " (fd):" : ":");
	for (const auto byte : frame.data)
		std::cout << ' ' << std::hex << std::setw(2) << std::setfill('0')
			  << static_cast<unsigned>(byte) << std::dec
			  << std::setfill(' ');
	std::cout << '\n';
}

}  // namespace

int main()
{
	try {
		const carrier::Thermometer thermometer{kHwmonDriver};
		std::cout << "Термодавач: " << thermometer.input_path() << '\n';

		try {
			std::cout << "Табличка з EEPROM: "
				  << carrier::read_board_id(
					     "/sys/bus/i2c/devices/1-0050/eeprom")
				  << '\n';
			const carrier::RtcClock rtc;
			std::cout << "Час PCF85063A (UTC): "
				  << carrier::format_utc(rtc.now()) << '\n';
		} catch (const std::exception& ex) {
			// Довідкові дані: без них монітор працює далі.
			std::cerr << "Довідка про плату недоступна: " << ex.what() << '\n';
		}

		carrier::FaultIndicator panel{kGpioChip, kFaultLed};
		print_claim(panel, kHeartbeatLed, "led-heartbeat (gpio-leds)");
		print_claim(panel, kUserButton, "button-user (gpio-keys)");

		std::optional<carrier::CanLink> can;
		try {
			can.emplace("can0");
		} catch (const std::exception& ex) {
			std::cerr << "CAN недоступний (" << ex.what()
				  << ") — далі без телеметрії\n";
		}

		install_handlers();
		std::cout << "Моніторинг пішов, зупинка — Ctrl+C\n"
			  << std::fixed << std::setprecision(2);

		bool fault = false;
		while (!stop_requested.load()) {
			double celsius{};
			try {
				celsius = thermometer.celsius();
			} catch (const std::exception& ex) {
				// Обрив на I2C зникає й повертається: не падаємо.
				std::cerr << "Читання температури: " << ex.what() << '\n';
				idle_second();
				continue;
			}

			if (!fault && celsius >= kTripOn) {
				fault = true;
				std::cout << "УВАГА: перегрів " << celsius
					  << " °C — вмикаємо аварійний світлодіод\n";
			} else if (fault && celsius <= kTripOff) {
				fault = false;
				std::cout << "Температура в нормі: " << celsius << " °C\n";
			}

			panel.set(fault);

			if (can) {
				try {
					can->send_status(celsius, fault);
					// Пауза циклу — це очікування на шині.
					if (const auto frame =
						    can->receive(std::chrono::seconds{1}))
						print_frame(*frame);
				} catch (const std::exception& ex) {
					std::cerr << "CAN: " << ex.what()
						  << " — від'єднуємось\n";
					can.reset();
				}
			} else {
				idle_second();
			}

			std::cout << "t = " << celsius << " °C, аварія: "
				  << (fault ? "так" : "ні") << '\n';
		}

		std::cout << "\nЗупинка: гасимо індикацію, віддаємо лінії й сокет\n";
		panel.set(false);
	} catch (const std::exception& ex) {
		std::cerr << "Монітор плати-носія: " << ex.what() << '\n';
		return EXIT_FAILURE;
	}

	return EXIT_SUCCESS;
}
