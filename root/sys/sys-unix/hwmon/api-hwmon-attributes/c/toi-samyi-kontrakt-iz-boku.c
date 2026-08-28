enum hwmon_sensor_types {
        hwmon_chip,        /* атрибути всієї мікросхеми, не каналу */
        hwmon_temp,        /* HWMON_T_*                            */
        hwmon_in,          /* HWMON_I_*                            */
        hwmon_curr,        /* HWMON_C_*                            */
        hwmon_power,       /* HWMON_P_*                            */
        hwmon_energy,      /* HWMON_E_*                            */
        hwmon_humidity,    /* HWMON_H_*                            */
        hwmon_fan,         /* HWMON_F_*                            */
        hwmon_pwm,         /* HWMON_PWM_*                          */
        hwmon_intrusion,   /* HWMON_INTRUSION_*                    */
        hwmon_max,
};
