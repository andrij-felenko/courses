#include <cstdint>
#include <cstddef>
#include <span>

namespace dma {

/* Регістрова структура одного каналу контролера DMA */
struct ChannelRegisters {
	volatile uint32_t CR;     /* Керуючий регістр каналу */
	volatile uint32_t NDTR;   /* Лічильник транзакцій */
	volatile uint32_t PAR;    /* Адреса периферійного пристрою */
	volatile uint32_t MAR;    /* Адреса комірки пам'яті */
	volatile uint32_t RESERVED;
};

/* Спільні регістри статусу та очищення прапорів */
struct ControllerRegisters {
	volatile uint32_t ISR;    /* Регістр прапорів переривань */
	volatile uint32_t IFCR;   /* Регістр скидання переривань */
};

/* Напрямок передачі даних */
enum class Direction : uint32_t {
	PeripheralToMemory = 0U << 4,
	MemoryToPeripheral = 1U << 4
};

/* Пріоритет каналу в арбітражі шини */
enum class Priority : uint32_t {
	Low      = 0U << 12,
	Medium   = 1U << 12,
	High     = 2U << 12,
	VeryHigh = 3U << 12
};

/* Бітові маски конфігурації */
inline constexpr uint32_t CR_EN   = 1U << 0;
inline constexpr uint32_t CR_TCIE = 1U << 1;
inline constexpr uint32_t CR_HTIE = 1U << 2;
inline constexpr uint32_t CR_TEIE = 1U << 3;
inline constexpr uint32_t CR_CIRC = 1U << 5;
inline constexpr uint32_t CR_MINC = 1U << 7;

inline void barrier_data() noexcept {
	__asm volatile("dmb 0xF" ::: "memory");
}

inline void barrier_sync() noexcept {
	__asm volatile("dsb 0xF" ::: "memory");
}

/* Покажчик на функцію зворотного виклику */
using Callback = void (*)(void* user_ctx);

/* RAII-клас керування кільцевим каналом DMA */
class CircularDmaReceiver {
public:
	CircularDmaReceiver(ChannelRegisters* channel,
	                    ControllerRegisters* controller,
	                    uint8_t channel_number) noexcept
		: channel_(channel),
		  controller_(controller),
		  channel_number_(channel_number) {}

	~CircularDmaReceiver() noexcept {
		stop();
	}

	/* Заборона копіювання для запобігання дублюванню монопольного доступу до каналу */
	CircularDmaReceiver(const CircularDmaReceiver&) = delete;
	CircularDmaReceiver& operator=(const CircularDmaReceiver&) = delete;

	/* Дозвіл семантики переміщення */
	CircularDmaReceiver(CircularDmaReceiver&& other) noexcept
		: channel_(other.channel_),
		  controller_(other.controller_),
		  channel_number_(other.channel_number_),
		  buffer_(other.buffer_),
		  on_half_(other.on_half_),
		  on_full_(other.on_full_),
		  on_error_(other.on_error_),
		  context_(other.context_) {
		other.channel_ = nullptr;
		other.controller_ = nullptr;
	}

	CircularDmaReceiver& operator=(CircularDmaReceiver&& other) noexcept {
		if (this != &other) {
			stop();
			channel_ = other.channel_;
			controller_ = other.controller_;
			channel_number_ = other.channel_number_;
			buffer_ = other.buffer_;
			on_half_ = other.on_half_;
			on_full_ = other.on_full_;
			on_error_ = other.on_error_;
			context_ = other.context_;
			other.channel_ = nullptr;
			other.controller_ = nullptr;
		}
		return *this;
	}

	bool init(uintptr_t periph_addr,
	          std::span<uint8_t> buffer,
	          Callback on_half,
	          Callback on_full,
	          Callback on_error,
	          void* context) noexcept {
		if (!channel_ || !controller_ || buffer.empty() || (buffer.size() % 2 != 0)) {
			return false;
		}

		buffer_ = buffer;
		on_half_ = on_half;
		on_full_ = on_full;
		on_error_ = on_error;
		context_ = context;

		/* Крок 1: Зупинка каналу */
		channel_->CR &= ~CR_EN;
		barrier_sync();
		while (channel_->CR & CR_EN) {
			/* Очікування повної зупинки автомата шини */
		}

		/* Крок 2: Очищення прапорів каналу */
		const uint32_t shift = (channel_number_ - 1U) * 4U;
		controller_->IFCR = (0xFU << shift);
		barrier_sync();

		/* Кроки 3-5: Налаштування адрес та обсягу передачі */
		channel_->PAR = static_cast<uint32_t>(periph_addr);
		channel_->MAR = reinterpret_cast<uint32_t>(buffer_.data());
		channel_->NDTR = static_cast<uint32_t>(buffer_.size());

		/* Крок 6: Конфігурація бітів керування */
		uint32_t cr_val = static_cast<uint32_t>(Direction::PeripheralToMemory) |
		                  static_cast<uint32_t>(Priority::VeryHigh) |
		                  CR_CIRC |
		                  CR_MINC |
		                  CR_TCIE |
		                  CR_HTIE |
		                  CR_TEIE;

		channel_->CR = cr_val;
		barrier_data();
		return true;
	}

	void start() noexcept {
		if (channel_) {
			barrier_sync();
			channel_->CR |= CR_EN;
			barrier_data();
		}
	}

	void stop() noexcept {
		if (channel_) {
			channel_->CR &= ~CR_EN;
			barrier_sync();
			while (channel_->CR & CR_EN) {
				/* Очікування переходу в безпечний стан */
			}
		}
	}

	[[nodiscard]] size_t get_head_index() const noexcept {
		if (!channel_ || buffer_.empty()) return 0;
		const uint32_t remaining = channel_->NDTR;
		return (remaining <= buffer_.size()) ? (buffer_.size() - remaining) : 0;
	}

	void handle_irq() noexcept {
		if (!channel_ || !controller_) return;

		const uint32_t shift = (channel_number_ - 1U) * 4U;
		const uint32_t status = controller_->ISR;

		if (status & (1U << (shift + 3))) { /* Transfer Error */
			controller_->IFCR = (1U << (shift + 3));
			barrier_sync();
			if (on_error_) on_error_(context_);
		}

		if (status & (1U << (shift + 2))) { /* Half Transfer */
			controller_->IFCR = (1U << (shift + 2));
			barrier_sync();
			if (on_half_) on_half_(context_);
		}

		if (status & (1U << (shift + 1))) { /* Transfer Complete */
			controller_->IFCR = (1U << (shift + 1));
			barrier_sync();
			if (on_full_) on_full_(context_);
		}
	}

private:
	ChannelRegisters*    channel_{nullptr};
	ControllerRegisters* controller_{nullptr};
	uint8_t              channel_number_{0};
	std::span<uint8_t>   buffer_{};
	Callback             on_half_{nullptr};
	Callback             on_full_{nullptr};
	Callback             on_error_{nullptr};
	void*                context_{nullptr};
};

} // namespace dma
