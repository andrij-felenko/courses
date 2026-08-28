namespace rtos {

class EventGroupIsrSetter {
public:
    explicit EventGroupIsrSetter(EventGroupHandle_t handle) noexcept : handle_(handle) {}

    bool set_bits(EventBits_t bits, BaseType_t* higher_priority_woken) noexcept {
        return xEventGroupSetBitsFromISR(handle_, bits, higher_priority_woken) == pdPASS;
    }

private:
    EventGroupHandle_t handle_;
};

} // namespace rtos
