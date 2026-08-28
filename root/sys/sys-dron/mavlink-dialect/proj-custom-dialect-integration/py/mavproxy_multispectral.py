"""
mavproxy_multispectral.py — Розширення консолі MAVProxy для спектральної камери.
"""
from MAVProxy.modules.lib import mp_module

class MultispectralModule(mp_module.MPModule):
    def __init__(self, mpstate):
        super(MultispectralModule, self).__init__(mpstate, "multispectral", "Підтримка спектральної камери")
        self.add_command('spectral', self.cmd_spectral, "Команди спектрального сенсора", ['trigger', 'status'])

    def cmd_spectral(self, args):
        if len(args) < 1:
            print("Використання: spectral trigger <exposure_ms> <filter_id>")
            return

        if args[0] == 'trigger':
            exp = float(args[1]) if len(args) > 1 else 50.0
            flt = float(args[2]) if len(args) > 2 else 1.0
            print(f"Відправка команди зйомки: експозиція {exp} мс, фільтр {flt}")
            self.master.mav.command_long_send(
                self.settings.target_system,
                100,  # Component ID
                42050, 0, exp, flt, 1.0, 0, 0, 0, 0
            )

    def mavlink_packet(self, msg):
        if msg.get_type() == 'MULTISPECTRAL_SURVEY_STATUS':
            # Логування кастомної телеметрії у фоновому режимі
            self.console.writeln(f"[СЕНСОР] T={msg.sensor_temperature:.1f}C NIR={msg.raw_channels[3]}", bg='black')

def init(mpstate):
    return MultispectralModule(mpstate)
