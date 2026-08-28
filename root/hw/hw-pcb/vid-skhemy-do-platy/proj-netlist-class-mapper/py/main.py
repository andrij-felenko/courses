import pcbnew

board = pcbnew.GetBoard()
design_settings = board.GetDesignSettings()

# Словник нових класів, згенерований утилітою
net_class_assignments = {
    "+3V3_SYS": "Power",
    "GND": "Power",
    "USB_D_P": "HighSpeed",
    "USB_D_N": "HighSpeed",
    "ADC_IN1_TEMP": "Analog"
}

for net_name, class_name in net_class_assignments.items():
    net = board.FindNet(net_name)
    if net:
        net.SetNetClassName(class_name)

pcbnew.Refresh()
