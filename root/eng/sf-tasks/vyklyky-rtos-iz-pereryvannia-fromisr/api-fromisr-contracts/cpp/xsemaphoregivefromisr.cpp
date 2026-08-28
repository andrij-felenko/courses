namespace rtos {

class BinarySemaphoreIsr {
public:
    explicit BinarySemaphoreIsr(SemaphoreHandle_t handle) noexcept : handle_(handle) {}

    [[nodiscard]] bool give(BaseType_t* higher_priority_woken) noexcept {
        return xSemaphoreGiveFromISR(handle_, higher_priority_woken) == pdPASS;
    }

private:
    SemaphoreHandle_t handle_;
};

} // namespace rtos
