struct thermal_trip {
    int temperature;        /* Поріг у m°C */
    int hysteresis;         /* Гістерезис у m°C */
    enum thermal_trip_type type;
    u8 flags;
};

struct thermal_zone_device_ops {
    int (*get_temp) (struct thermal_zone_device *, int *);
    int (*set_trips) (struct thermal_zone_device *, int, int);
    int (*change_mode) (struct thermal_zone_device *, enum thermal_device_mode);
    int (*set_trip_temp) (struct thermal_zone_device *, int, int);
};

struct thermal_zone_device *
thermal_zone_device_register_with_trips(const char *type,
                                        const struct thermal_trip *trips,
                                        int num_trips,
                                        unsigned int mask,
                                        void *devdata,
                                        const struct thermal_zone_device_ops *ops,
                                        const struct thermal_zone_params *tzp,
                                        int passive_delay,
                                        int polling_delay);
