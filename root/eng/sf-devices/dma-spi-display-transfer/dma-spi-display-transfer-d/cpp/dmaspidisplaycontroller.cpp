#include <cstdint>
#include <type_traits>

/* Шаблонний драйвер прямого доступу до апаратних регістрів мікроконтролера */
template <uintptr_t SpiBase, uintptr_t DmaBase, uintptr_t GpioBase>
class DmaSpiDisplayController {
public:
	struct WindowCoordinates {
		uint16_t x0;
		uint16_t y0;
		uint16_t x1;
		uint16_t y1;
	};

	using NotificationCallback = void (*)(void* context);

	DmaSpiDisplayController(uint32_t dcPin, uint32_t csPin) noexcept
		: m_dcPinMask(1UL << dcPin)
		, m_csPinMask(1UL << csPin)
		, m_isBusy(false)
		, m_callback(nullptr)
		, m_callbackContext(nullptr) {}

	void init() noexcept {
		regDmaCpar() = reinterpret_cast<uint32_t>(&regSpiDr());
	}

	void setWindow(const WindowCoordinates& coords) noexcept {
		sendCommand(0x2A); /* Column Address Set */
		sendData16(coords.x0);
		sendData16(coords.x1);

		sendCommand(0x2B); /* Page Address Set */
		sendData16(coords.y0);
		sendData16(coords.y1);

		sendCommand(0x2C); /* Memory Write */
	}

	bool transmitBufferAsync(const uint16_t* buffer, uint32_t count,
	                         NotificationCallback cb, void* ctx) noexcept {
		if (m_isBusy || buffer == nullptr || count == 0) {
			return false;
		}

		m_isBusy = true;
		m_callback = cb;
		m_callbackContext = ctx;

		regDmaCcr() &= ~DmaCcrEn;
		regDmaCmar() = reinterpret_cast<uint32_t>(buffer);
		regDmaCndtr() = count;

		/* Конфігурація 16-бітної передачі з найвищим пріоритетом Very High */
		regDmaCcr() = DmaCcrDirM2P | DmaCcrMinc |
		              DmaCcrPsize16 | DmaCcrMsize16 |
		              DmaCcrPlVHigh | DmaCcrTcie;

		regSpiCr2() |= SpiCr2TxDmaEn;
		regDmaCcr() |= DmaCcrEn;

		return true;
	}

	void handleInterrupt() noexcept {
		/* Перевірка біта завершення передачі каналу 3 у регістрі ISR */
		if (regDmaIsr() & (1UL << 9)) {
			regDmaIfcr() = (1UL << 9);
			regSpiCr2() &= ~SpiCr2TxDmaEn;

			while (regSpiSr() & SpiSrBsy);
			setChipSelect(false);

			m_isBusy = false;

			if (m_callback != nullptr) {
				m_callback(m_callbackContext);
			}
		}
	}

	[[nodiscard]] bool isBusy() const noexcept {
		return m_isBusy;
	}

private:
	static constexpr uint32_t SpiCr2TxDmaEn = (1UL << 1);
	static constexpr uint32_t SpiSrBsy      = (1UL << 7);
	static constexpr uint32_t SpiSrTxe      = (1UL << 1);

	static constexpr uint32_t DmaCcrEn      = (1UL << 0);
	static constexpr uint32_t DmaCcrTcie    = (1UL << 1);
	static constexpr uint32_t DmaCcrDirM2P  = (1UL << 4);
	static constexpr uint32_t DmaCcrMinc    = (1UL << 7);
	static constexpr uint32_t DmaCcrPsize16 = (1UL << 8);
	static constexpr uint32_t DmaCcrMsize16 = (1UL << 10);
	static constexpr uint32_t DmaCcrPlVHigh = (3UL << 12);

	const uint32_t m_dcPinMask;
	const uint32_t m_csPinMask;
	volatile bool m_isBusy;
	NotificationCallback m_callback;
	void* m_callbackContext;

	/* Допоміжні методи прямого доступу до пам'яті регістрів */
	static volatile uint32_t& reg(uintptr_t addr) noexcept {
		return *reinterpret_cast<volatile uint32_t*>(addr);
	}

	static volatile uint32_t& regSpiSr()   noexcept { return reg(SpiBase + 0x08UL); }
	static volatile uint32_t& regSpiDr()   noexcept { return reg(SpiBase + 0x0CUL); }
	static volatile uint32_t& regSpiCr2()  noexcept { return reg(SpiBase + 0x04UL); }
	static volatile uint32_t& regDmaIsr()  noexcept { return reg(DmaBase + 0x00UL); }
	static volatile uint32_t& regDmaIfcr() noexcept { return reg(DmaBase + 0x04UL); }
	static volatile uint32_t& regDmaCcr()  noexcept { return reg(DmaBase + 0x08UL); }
	static volatile uint32_t& regDmaCndtr()noexcept { return reg(DmaBase + 0x0CUL); }
	static volatile uint32_t& regDmaCpar() noexcept { return reg(DmaBase + 0x10UL); }
	static volatile uint32_t& regDmaCmar() noexcept { return reg(DmaBase + 0x14UL); }
	static volatile uint32_t& regGpioBsrr()noexcept { return reg(GpioBase + 0x10UL); }

	void sendCommand(uint8_t cmd) noexcept {
		while (regSpiSr() & SpiSrBsy);
		regGpioBsrr() = (m_dcPinMask << 16); /* DC Low */
		setChipSelect(true);
		regSpiDr() = cmd;
		while (!(regSpiSr() & SpiSrTxe));
		while (regSpiSr() & SpiSrBsy);
		regGpioBsrr() = m_dcPinMask;         /* DC High */
	}

	void sendData16(uint16_t data) noexcept {
		regSpiDr() = (data >> 8);
		while (!(regSpiSr() & SpiSrTxe));
		regSpiDr() = (data & 0xFF);
		while (!(regSpiSr() & SpiSrTxe));
		while (regSpiSr() & SpiSrBsy);
	}

	void setChipSelect(bool active) noexcept {
		if (active) {
			regGpioBsrr() = (m_csPinMask << 16); /* CS Low */
		} else {
			regGpioBsrr() = m_csPinMask;         /* CS High */
		}
	}
};
