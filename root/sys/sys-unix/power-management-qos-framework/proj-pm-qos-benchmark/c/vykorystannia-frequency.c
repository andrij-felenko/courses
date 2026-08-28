#include <linux/cpufreq.h>
#include <linux/pm_qos.h>

static struct freq_qos_request my_freq_req;

void my_driver_boost_frequency(struct cpufreq_policy *policy, u32 min_freq_khz) {
    // Додаємо вимогу мінімальної частоти у кГц для політики cpufreq
    freq_qos_add_request(&policy->constraints, &my_freq_req, FREQ_QOS_MIN, min_freq_khz);
}

void my_driver_unboost_frequency(void) {
    // Видаляємо вимогу мінімальної частоти
    freq_qos_remove_request(&my_freq_req);
}
