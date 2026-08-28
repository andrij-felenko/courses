#include <esp_matter.h>
#include <esp_matter_endpoint.h>
#include <esp_log.h>

using namespace esp_matter;
using namespace esp_matter::attribute;   // callback_type_t, PRE_UPDATE, update()
using namespace esp_matter::endpoint;
using namespace chip::app::Clusters;     // тут живуть Thermostat::Id тощо

static const char *TAG = "thermostat";

// Номер НАШОГО прикладного endpoint. Заповниться при створенні —
// нам він потрібен, щоб пізніше адресувати attribute::update саме сюди.
static uint16_t s_endpoint_id = 0;

extern "C" void app_main(void)
{
    // 1. Вузол. Два обробники йдуть у node::create назавжди:
    //    attribute_update_cb — коли контролер пише в атрибут (дорога ВНИЗ);
    //    identification_cb    — коли контролер просить пристрій «блимнути собою».
    node::config_t node_config;
    node_t *node = node::create(&node_config,
                                app_attribute_update_cb,
                                app_identification_cb,
                                /*priv_data=*/NULL);
    if (node == NULL) {
        ESP_LOGE(TAG, "не вдалося створити node");
        return;
    }

    // 2. Endpoint термостата = цеглинка device type 0x0301 разом із
    //    її ОБОВ'ЯЗКОВИМ кластером Thermostat (0x0201). Стартові значення
    //    атрибутів задаємо тут-таки, у config — до створення.
    thermostat::config_t ep_config;
    ep_config.thermostat.local_temperature            = 2100;  // 21.00 °C, соті!
    ep_config.thermostat.system_mode                  = 4;      // 4 = Heat
    ep_config.thermostat.control_sequence_of_operation = 2;     // тільки нагрів
    // фіча «нагрів» вмикає атрибут OccupiedHeatingSetpoint у цьому кластері:
    ep_config.thermostat.feature_flags =
        cluster::thermostat::feature::heating::get_id();

    endpoint_t *endpoint =
        thermostat::create(node, &ep_config, ENDPOINT_FLAG_NONE, /*priv=*/NULL);
    if (endpoint == NULL) {
        ESP_LOGE(TAG, "не вдалося створити endpoint термостата");
        return;
    }

    // 3. Докладаємо ДРУГУ цеглинку — вимірювання температури (0x0402).
    //    Тип «термостат» її не вимагає, тож додаємо кластер руками —
    //    серверною стороною (ми ТРИМАЄМО значення й віддаємо його).
    cluster::temperature_measurement::config_t tm_config;
    tm_config.measured_value     = 2100;    // те саме 21.00 °C у сотих
    tm_config.min_measured_value = -5000;   // -50.00 °C — межа нашого давача
    tm_config.max_measured_value =  8000;   //  80.00 °C
    cluster::temperature_measurement::create(endpoint, &tm_config,
                                             CLUSTER_FLAG_SERVER);

    // 4. Запам'ятовуємо НОМЕР endpoint. SDK сам призначив його (буде 1) —
    //    ми не хардкодимо одиницю, а питаємо, бо порядок створення вирішує.
    s_endpoint_id = endpoint::get_id(endpoint);
    ESP_LOGI(TAG, "endpoint термостата = %u", s_endpoint_id);

    // 5. Старт стеку. ДО цього рядка — тільки будували дерево;
    //    ПІСЛЯ — Matter живе: слухає мережу, чекає приєднання по QR-коду.
    esp_matter::start(app_event_cb);
}
