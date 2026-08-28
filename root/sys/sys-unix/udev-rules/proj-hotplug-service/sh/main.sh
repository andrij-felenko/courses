$ systemctl list-units --type=device 'dev-ttyUSB*'
UNIT               LOAD   ACTIVE SUB     DESCRIPTION
dev-ttyUSB0.device loaded active plugged FT232 USB-Serial

$ systemctl is-active laser-agent@ttyUSB0.service
active

# висмикнули шнур
$ systemctl is-active laser-agent@ttyUSB0.service
inactive
