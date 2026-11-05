#include <cstdint>
#include <cstddef>
#include <array>
#include <atomic>

template <size_t BufferHalfSize, size_t AxisCount>
class DmaStepController {
public:
	static constexpr size_t TotalBufferSize = BufferHalfSize * 2;

	struct AxisHardwareConfig {
		uint32_t step_mask;    /* Розряди 0..15 регістра BSRR для піна STEP */
		uint32_t dir_mask;     /* Розряди 0..15 регістра BSRR для піна DIR */
		bool initial_dir;      /* Початковий стан лінії DIR */
	};

	explicit DmaStepController(volatile uint32_t* target_bsrr, const std::array<AxisHardwareConfig, AxisCount>& axes)
		: target_bsrr_(target_bsrr), axes_(axes), step_reset_mask_(0), dir_hold_mask_(0), underrun_flag_(false) {
		for (const auto& axis : axes_) {
			step_reset_mask_ |= (axis.step_mask << 16);
			if (axis.initial_dir) {
				dir_hold_mask_ |= axis.dir_mask;
			} else {
				dir_hold_mask_ |= (axis.dir_mask << 16);
			}
		}

		segment_ready_[0].store(false, std::memory_order_relaxed);
		segment_ready_[1].store(false, std::memory_order_relaxed);

		const uint32_t idle_pattern = step_reset_mask_ | dir_hold_mask_;
		dma_buffer_.fill(idle_pattern);
	}

	/* Наповнення розрахункового сегмента масками кроків */
	void fill_segment(size_t segment_idx, const uint32_t* patterns, size_t count) noexcept {
		if (segment_idx > 1 || count > BufferHalfSize) return;

		uint32_t* dest = &dma_buffer_[segment_idx * BufferHalfSize];
		for (size_t i = 0; i < count; ++i) {
			dest[i] = patterns[i];
		}

		const uint32_t idle_pattern = step_reset_mask_ | dir_hold_mask_;
		for (size_t i = count; i < BufferHalfSize; ++i) {
			dest[i] = idle_pattern;
		}

		/* Впорядкування пам'яті: публікація сегмента перед встановленням прапорця */
		segment_ready_[segment_idx].store(true, std::memory_order_release);
	}

	/* Обробник переривання DMA (події половинної та повної передачі) */
	void on_dma_interrupt(bool is_full_transfer) noexcept {
		const size_t consumed = is_full_transfer ? 1 : 0;
		const size_t next_seg = is_full_transfer ? 0 : 1;

		segment_ready_[consumed].store(false, std::memory_order_release);

		/* Перевірка наявності підготовлених даних для наступного півбуфера */
		if (!segment_ready_[next_seg].load(std::memory_order_acquire)) {
			underrun_flag_.store(true, std::memory_order_relaxed);
			uint32_t* dest = &dma_buffer_[next_seg * BufferHalfSize];
			const uint32_t idle_pattern = step_reset_mask_ | dir_hold_mask_;

			for (size_t i = 0; i < BufferHalfSize; ++i) {
				dest[i] = idle_pattern;
			}
		}
	}

	/* Апаратна аварійна зупинка */
	void emergency_abort() noexcept {
		if (target_bsrr_) {
			*target_bsrr_ = step_reset_mask_;
		}
	}

	[[nodiscard]] bool check_and_clear_underrun() noexcept {
		return underrun_flag_.exchange(false, std::memory_order_relaxed);
	}

	[[nodiscard]] uint32_t* raw_buffer_ptr() noexcept {
		return dma_buffer_.data();
	}

private:
	volatile uint32_t* target_bsrr_;
	std::array<AxisHardwareConfig, AxisCount> axes_;
	std::array<uint32_t, TotalBufferSize> dma_buffer_;
	std::array<std::atomic<bool>, 2> segment_ready_;
	std::atomic<bool> underrun_flag_;
	uint32_t step_reset_mask_;
	uint32_t dir_hold_mask_;
};
