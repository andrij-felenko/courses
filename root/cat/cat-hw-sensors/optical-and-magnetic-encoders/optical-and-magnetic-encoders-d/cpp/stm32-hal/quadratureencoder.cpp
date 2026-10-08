// Клас-обгортка квадратурного декодера таймера STM32 на C++
class QuadratureEncoder {
public:
    explicit QuadratureEncoder(TIM_HandleTypeDef* htim) : m_htim(htim) {}

    void start() {
        HAL_TIM_Encoder_Start(m_htim, TIM_CHANNEL_ALL);
    }

    int32_t getCount() const {
        return static_cast<int32_t>(__HAL_TIM_GET_COUNTER(m_htim));
    }

    int8_t getDirection() const {
        return __HAL_TIM_IS_TIM_COUNTING_DOWN(m_htim) ? -1 : 1;
    }

private:
    TIM_HandleTypeDef* m_htim;
};
