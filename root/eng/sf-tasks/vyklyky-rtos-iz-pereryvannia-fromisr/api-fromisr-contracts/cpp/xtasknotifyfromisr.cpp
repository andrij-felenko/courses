namespace rtos {

class AdvancedTaskNotifier {
public:
    explicit AdvancedTaskNotifier(TaskHandle_t target_task) noexcept : target_(target_task) {}

    bool set_bits(uint32_t bits, BaseType_t* higher_priority_woken) noexcept {
        return xTaskNotifyFromISR(target_, bits, eSetBits, higher_priority_woken) == pdPASS;
    }

    bool overwrite_value(uint32_t val, BaseType_t* higher_priority_woken) noexcept {
        return xTaskNotifyFromISR(target_, val, eSetValueWithOverwrite, higher_priority_woken) == pdPASS;
    }

private:
    TaskHandle_t target_;
};

} // namespace rtos
