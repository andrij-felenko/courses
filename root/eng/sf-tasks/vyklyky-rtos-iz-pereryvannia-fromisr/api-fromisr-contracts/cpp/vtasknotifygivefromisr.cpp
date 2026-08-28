namespace rtos {

class TaskNotifier {
public:
    explicit TaskNotifier(TaskHandle_t target_task) noexcept : target_(target_task) {}

    void notify_give(BaseType_t* higher_priority_woken) noexcept {
        vTaskNotifyGiveFromISR(target_, higher_priority_woken);
    }

private:
    TaskHandle_t target_;
};

} // namespace rtos
