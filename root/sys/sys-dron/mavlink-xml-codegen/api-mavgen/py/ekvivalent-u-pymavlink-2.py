def attitude_encode(self, time_boot_ms, roll, pitch, yaw,
                    rollspeed, pitchspeed, yawspeed):
    return MAVLink_attitude_message(time_boot_ms, roll, pitch, yaw,
                                    rollspeed, pitchspeed, yawspeed)

def attitude_send(self, time_boot_ms, roll, pitch, yaw,
                  rollspeed, pitchspeed, yawspeed, force_mavlink1=False):
    self.send(self.attitude_encode(time_boot_ms, roll, pitch, yaw,
                                   rollspeed, pitchspeed, yawspeed),
              force_mavlink1=force_mavlink1)
