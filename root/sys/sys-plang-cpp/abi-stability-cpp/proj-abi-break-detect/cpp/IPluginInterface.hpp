// IPluginInterface.hpp — COM-подібний абстрактний інтерфейс розширення
#pragma once
#include <cstdint>
#include <cstddef>

// Унікальні ідентифікатори інтерфейсів (Interface IDs)
constexpr uint32_t IID_PROCESSOR_V1 = 0x1001;
constexpr uint32_t IID_PARAM_CONTROLLER_V1 = 0x1002;

struct IPluginBase {
    // Слот 0: Запит підтримуваних інтерфейсів без порушення vtable
    virtual int32_t query_interface(uint32_t iid, void** out_interface) noexcept = 0;

    // Слот 1: Метод вивільнення екземпляра
    virtual void release() noexcept = 0;

protected:
    ~IPluginBase() = default;
};

struct IProcessorV1 : public IPluginBase {
    // Слот 2: Ініціалізація
    virtual int32_t initialize(const char* name) = 0;

    // Слот 3: Основний цикл обробки
    virtual int32_t process_frame(const float* in, float* out, size_t count) = 0;
};

struct IParameterController : public IPluginBase {
    // Слот 2 для IParameterController: керування параметрами
    virtual int32_t set_parameter(uint32_t param_id, double value) = 0;
    virtual double  get_parameter(uint32_t param_id) = 0;
};
