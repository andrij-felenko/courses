#include <cstdint>
#include <cstddef>
#include <array>
#include <atomic>
#include <type_traits>

namespace trace {

/* Апаратні адреси ядра ARM Cortex-M */
inline volatile uint32_t& reg_dwt_cyccnt = *reinterpret_cast<volatile uint32_t*>(0xE0001004);
inline volatile uint32_t& reg_itm_port0  = *reinterpret_cast<volatile uint32_t*>(0xE0000000);
inline volatile uint32_t& reg_itm_ter    = *reinterpret_cast<volatile uint32_t*>(0xE0000E00);
inline volatile uint32_t& reg_itm_tcr    = *reinterpret_cast<volatile uint32_t*>(0xE0000E80);

template <size_t Capacity = 512>
class HardwareTraceLogger {
	static_assert((Capacity & (Capacity - 1)) == 0, "Розмір буфера має бути степенем двійки");

public:
	constexpr HardwareTraceLogger() : head_(0), tail_(0), last_ticks_(0), dropped_(0) {}

	/* Швидкий вивід події через апаратний порт ITM */
	template <typename T>
	static bool emit_itm(uint16_t event_id, T payload) {
		static_assert(sizeof(T) <= sizeof(uint32_t), "Розмір аргументу не повинен перевищувати 32 біти");
		if ((reg_itm_tcr & 1UL) && (reg_itm_ter & 1UL)) {
			if (reg_itm_port0 == 0) {
				return false;
			}
			*reinterpret_cast<volatile uint16_t*>(0xE0000000) = event_id;
			while (reg_itm_port0 == 0);
			reg_itm_port0 = static_cast<uint32_t>(payload);
			return true;
		}
		return false;
	}

	/* Атомарний запис події в буфер із дельта-компресією мітки часу */
	template <typename... Args>
	bool log(uint16_t event_id, Args... args) {
		constexpr size_t payload_len = (sizeof(Args) + ... + 0);
		constexpr size_t frame_len = sizeof(uint16_t) + sizeof(uint16_t) + payload_len;

		uint32_t now = reg_dwt_cyccnt;
		uint32_t prev = last_ticks_.load(std::memory_order_relaxed);
		uint16_t delta_time = static_cast<uint16_t>((now - prev) & 0xFFFF);
		last_ticks_.store(now, std::memory_order_relaxed);

		uint32_t current_head = head_.load(std::memory_order_relaxed);
		uint32_t current_tail = tail_.load(std::memory_order_acquire);

		if ((Capacity - (current_head - current_tail)) < frame_len) {
			dropped_.fetch_add(1, std::memory_order_relaxed);
			return false;
		}

		/* Збереження заголовка та часу */
		write_u16(current_head, event_id);
		write_u16(current_head + 2, delta_time);

		size_t offset = 4;
	\tauto serialize = [this, current_head, &offset](const auto& val) {
			using ValueType = std::decay_t<decltype(val)>;
			const auto* bytes = reinterpret_cast<const uint8_t*>(&val);
			for (size_t i = 0; i < sizeof(ValueType); ++i) {
				this->write_byte(current_head + offset + i, bytes[i]);
			}
			offset += sizeof(ValueType);
		};

		(serialize(args), ...);

		/* Публікація зарезервованої ділянки для читача */
		head_.store(current_head + frame_len, std::memory_order_release);
		return true;
	}

	uint32_t get_dropped_count() const {
		return dropped_.load(std::memory_order_relaxed);
	}

private:
	void write_byte(size_t index, uint8_t val) {
		buffer_[index & (Capacity - 1)] = val;
	}

	void write_u16(size_t index, uint16_t val) {
		write_byte(index, static_cast<uint8_t>(val & 0xFF));
		write_byte(index + 1, static_cast<uint8_t>(val >> 8));
	}

	alignas(4) std::array<uint8_t, Capacity> buffer_{};
	std::atomic<uint32_t> head_;
	std::atomic<uint32_t> tail_;
	std::atomic<uint32_t> last_ticks_;
	std::atomic<uint32_t> dropped_;
};

} // namespace trace
