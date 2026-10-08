// C++ (RAII / SCPI): Клас автоматизованого налаштування тригера осцилографа
#include <string>
#include <stdexcept>
#include <visa.h>

class OscilloscopeTriggerController {
private:
    ViSession vi_;
public:
    explicit OscilloscopeTriggerController(ViSession vi) : vi_(vi) {}

    void setupNormalBurstTrigger(double levelVolts, double holdoffSeconds) {
        std::string cmd = "TRIGger:A:MODE NORMal\n";
        cmd += "TRIGger:A:TYPE EDGE\n";
        cmd += "TRIGger:A:LEVel " + std::to_string(levelVolts) + "\n";
        cmd += "TRIGger:A:COUPling HFRej\n";
        cmd += "TRIGger:A:HOLDoff " + std::to_string(holdoffSeconds) + "\n";
        
        ViStatus status = viWrite(vi_, (ViBuf)cmd.c_str(), (ViUInt32)cmd.size(), VI_NULL);
        if (status < VI_SUCCESS) {
            throw std::runtime_error("Помилка відправки SCPI-команд тригеризації");
        }
    }
};
