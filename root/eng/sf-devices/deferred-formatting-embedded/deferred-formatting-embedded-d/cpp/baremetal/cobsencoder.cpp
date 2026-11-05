#include <cstdint>
#include <cstddef>
#include <span>
#include <array>

namespace diagnostic {

class CobsEncoder {
public:
	static constexpr uint8_t Delimiter = 0x00;

	/* Кодування послідовності байтів у вихідний буфер */
	static size_t encode(std::span<const uint8_t> input, std::span<uint8_t> output) {
		if (output.size() < (input.size() + input.size() / 254 + 2)) {
			return 0;
		}

		size_t read_pos = 0;
		size_t write_pos = 1;
		size_t code_pos = 0;
		uint8_t code = 1;

		while (read_pos < input.size()) {
			uint8_t byte = input[read_pos++];
			if (byte == 0) {
				output[code_pos] = code;
				code_pos = write_pos++;
				code = 1;
			} else {
				output[write_pos++] = byte;
				if (++code == 0xFF) {
					output[code_pos] = code;
					code_pos = write_pos++;
					code = 1;
				}
			}
		}

		output[code_pos] = code;
		output[write_pos++] = Delimiter;
		return write_pos;
	}
};

struct alignas(4) CrashRecord {
	uint32_t r0;
	uint32_t r1;
	uint32_t r2;
	uint32_t r3;
	uint32_t r12;
	uint32_t lr;
	uint32_t pc;
	uint32_t psr;
	uint32_t cfsr;
	uint32_t hfsr;
	uint32_t magic;
};

/* Спеціальний розмір і атрибут noinit */
inline constexpr uint32_t CrashMagic = 0xDEADBEEF;
[[gnu::section(".noinit")]] inline CrashRecord g_retained_crash;

class EmergencyLogger {
public:
	static void capture_and_transmit(uint16_t event_id, const uint32_t* stack_ptr) {
		volatile uint32_t* const uart_dr = reinterpret_cast<volatile uint32_t*>(0x40013804);
		volatile uint32_t* const uart_sr = reinterpret_cast<volatile uint32_t*>(0x40013800);

		g_retained_crash.r0 = stack_ptr[0];
		g_retained_crash.r1 = stack_ptr[1];
		g_retained_crash.r2 = stack_ptr[2];
		g_retained_crash.r3 = stack_ptr[3];
		g_retained_crash.r12 = stack_ptr[4];
		g_retained_crash.lr = stack_ptr[5];
		g_retained_crash.pc = stack_ptr[6];
		g_retained_crash.psr = stack_ptr[7];
		g_retained_crash.cfsr = *reinterpret_cast<volatile uint32_t*>(0xE000ED28);
		g_retained_crash.hfsr = *reinterpret_cast<volatile uint32_t*>(0xE000ED2C);
		g_retained_crash.magic = CrashMagic;

	\tauto send_byte = [uart_dr, uart_sr](uint8_t byte) {
			while (!(*uart_sr & (1UL << 7)));
			*uart_dr = byte;
		};

		send_byte(static_cast<uint8_t>(event_id & 0xFF));
		send_byte(static_cast<uint8_t>(event_id >> 8));
	}
};

} // namespace diagnostic
