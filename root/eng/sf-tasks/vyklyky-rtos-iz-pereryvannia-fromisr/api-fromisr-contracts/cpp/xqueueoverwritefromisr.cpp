namespace rtos {

template <typename T>
class MailboxIsrEndpoint {
public:
    explicit MailboxIsrEndpoint(QueueHandle_t handle) noexcept : handle_(handle) {}

    void overwrite(const T& item, BaseType_t* higher_priority_woken) noexcept {
        xQueueOverwriteFromISR(handle_, &item, higher_priority_woken);
    }

private:
    QueueHandle_t handle_;
};

} // namespace rtos
