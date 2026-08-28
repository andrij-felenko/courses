// Простий ПІ-регулятор струму переносу: тримати I_meas біля I_target.
typedef struct {
    uint16_t target_ma;     // бажаний струм переносу, мА
    int32_t  integ;         // накопичена інтегральна складова
    uint16_t duty;          // поточна шпаруватість ШІМ, 0..DUTY_MAX
} current_loop_t;

#define DUTY_MAX     1000
#define KP_NUM       3       // пропорційний коеф. (чисельник/знаменник — цілочисельно)
#define KP_DEN       10
#define KI_NUM       1
#define KI_DEN       50

extern uint16_t read_transfer_current_ma(void);   // струм по шунту
extern void     set_transfer_duty(uint16_t duty); // задати шпаруватість ключів

void current_loop_step(current_loop_t *cl)
{
    int32_t meas = read_transfer_current_ma();
    int32_t err  = (int32_t)cl->target_ma - meas;        // як далеко від цілі

    cl->integ += err;
    // анти-windup: не даємо інтегралу розпухнути за межі корисного діапазону
    if (cl->integ >  (int32_t)DUTY_MAX * KI_DEN) cl->integ =  (int32_t)DUTY_MAX * KI_DEN;
    if (cl->integ < -(int32_t)DUTY_MAX * KI_DEN) cl->integ = -(int32_t)DUTY_MAX * KI_DEN;

    int32_t duty = (err * KP_NUM) / KP_DEN + (cl->integ * KI_NUM) / KI_DEN;

    if (duty < 0)         duty = 0;
    if (duty > DUTY_MAX)  duty = DUTY_MAX;
    cl->duty = (uint16_t)duty;
    set_transfer_duty(cl->duty);
}
