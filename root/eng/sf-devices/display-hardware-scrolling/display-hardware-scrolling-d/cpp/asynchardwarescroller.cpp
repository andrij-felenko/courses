#include <cstdint>
#include <array>
#include <span>

class AsyncHardwareScroller {
public:
	enum class Command : uint8_t {
		ColumnAddressSet = 0x2A,
		RowAddressSet    = 0x2B,
		MemoryWrite      = 0x2C,
		VerticalScrollDef  = 0x33,
		VerticalScrollAddr = 0x37
	};

	static constexpr size_t kWidth = 240;
	static constexpr size_t kHeight = 320;
	static constexpr size_t kCacheAlignment = 32;

	AsyncHardwareScroller(uint16_t tfa, uint16_t vsa, uint16_t bfa) noexcept
		: tfa_(tfa), vsa_(vsa), bfa_(bfa), current_vsp_(tfa), active_idx_(0) {}

	void init() noexcept {
		const uint8_t def_payload[6] = {
			static_cast<uint8_t>(tfa_ >> 8), static_cast<uint8_t>(tfa_ & 0xFF),
			static_cast<uint8_t>(vsa_ >> 8), static_cast<uint8_t>(vsa_ & 0xFF),
			static_cast<uint8_t>(bfa_ >> 8), static_cast<uint8_t>(bfa_ & 0xFF)
		};
		writeCommand(Command::VerticalScrollDef);
		writeData(def_payload);
		updateScrollAddress(current_vsp_);
	}

	[[nodiscard]] std::span<uint16_t, kWidth> currentWriteBuffer() noexcept {
		return std::span<uint16_t, kWidth>(buffers_[active_idx_].data(), kWidth);
	}

	void commitLineAndScroll() noexcept {
		// Очікування імпульсу вертикальної гасільної паузи від виводу TE
		waitForTearingEffectInterrupt();

		// Фізичний рядок пам'яті GRAM, який вивільняється для нового запису
		const uint16_t physical_write_row = current_vsp_;

		// Інкремент стартової адреси розгортки з циклічним зацикленням у межах VSA
		current_vsp_++;
		if (current_vsp_ >= (tfa_ + vsa_)) {
			current_vsp_ = tfa_;
		}
		updateScrollAddress(current_vsp_);

		// Очікування завершення попередньої передачі каналом DMA
		waitForDmaReady();

		// Адресація одного вивільненого рядка у контролері дисплея
		setSingleRowWindow(physical_write_row);
		writeCommand(Command::MemoryWrite);

		// Виштовхування кеш-рядків для збереження узгодженості пам'яті
		flushCache(buffers_[active_idx_].data(), kWidth * sizeof(uint16_t));

		// Апаратний старт передачі масиву пікселів через DMA без блокування CPU
		startDmaTransfer(buffers_[active_idx_].data(), kWidth * sizeof(uint16_t));

		// Ротація індексу човникового буфера для наступного кроку рендерингу
		active_idx_ ^= 1;
	}

private:
	const uint16_t tfa_;
	const uint16_t vsa_;
	const uint16_t bfa_;
	uint16_t current_vsp_;
	uint8_t active_idx_;

	alignas(kCacheAlignment) std::array<std::array<uint16_t, kWidth>, 2> buffers_{};

	void updateScrollAddress(uint16_t vsp) noexcept {
		const uint8_t addr_bytes[2] = {
			static_cast<uint8_t>(vsp >> 8),
			static_cast<uint8_t>(vsp & 0xFF)
		};
		writeCommand(Command::VerticalScrollAddr);
		writeData(addr_bytes);
	}

	void setSingleRowWindow(uint16_t row) noexcept {
		const uint8_t col_box[4] = { 0, 0, static_cast<uint8_t>((kWidth - 1) >> 8), static_cast<uint8_t>((kWidth - 1) & 0xFF) };
		const uint8_t row_box[4] = { static_cast<uint8_t>(row >> 8), static_cast<uint8_t>(row & 0xFF),
		                             static_cast<uint8_t>(row >> 8), static_cast<uint8_t>(row & 0xFF) };

		writeCommand(Command::ColumnAddressSet);
		writeData(col_box);
		writeCommand(Command::RowAddressSet);
		writeData(row_box);
	}

	// Низькорівневі виклики платформи реалізуються у BSP цільового мікроконтролера
	void writeCommand(Command cmd) noexcept;
	void writeData(std::span<const uint8_t> data) noexcept;
	void waitForTearingEffectInterrupt() noexcept;
	void waitForDmaReady() noexcept;
	void flushCache(const void* ptr, size_t size) noexcept;
	void startDmaTransfer(const void* ptr, size_t size) noexcept;
};
