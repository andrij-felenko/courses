bool analyze_log_stream(const blackbox_frame_t* frames, size_t frame_count,
                        const analyzer_config_t* config,
                        crash_incident_report_t* report) {
    if (!frames || frame_count < 2 || !config || !report) {
        return false;
    }

    report->start_time_us = 0;
    report->end_time_us = 0;
    report->flags = ANOMALY_NONE;
    report->failed_motor_index = 0xFF;
    report->max_error_deg = 0.0f;
    report->min_vbat_v = 100.0f;

    uint64_t desync_start_time[MAX_MOTORS] = {0};
    uint64_t tracking_loss_start_time = 0;
    bool in_incident = false;

    for (size_t i = 1; i < frame_count; ++i) {
        const blackbox_frame_t* prev = &frames[i - 1];
        const blackbox_frame_t* curr = &frames[i];

        float dt = (float)(curr->timestamp_us - prev->timestamp_us) * 1e-6f;
        if (dt <= 0.0f || dt > 0.05f) {
            continue; /* Пропуск розривів часу */
        }

        if (curr->vbat_v < report->min_vbat_v) {
            report->min_vbat_v = curr->vbat_v;
        }

        /* 1. Перевірка просідання батареї у Brownout */
        if (curr->vbat_v < config->brownout_voltage_threshold_v) {
            report->flags |= ANOMALY_BROWNOUT;
            if (!in_incident) {
                report->start_time_us = curr->timestamp_us;
                in_incident = true;
            }
            report->end_time_us = curr->timestamp_us;
        }

        /* 2. Обчислення кутової похибки стеження */
        float err_roll = fabsf(curr->setpoint_rate[AXIS_ROLL] - curr->gyro_rate[AXIS_ROLL]);
        float err_pitch = fabsf(curr->setpoint_rate[AXIS_PITCH] - curr->gyro_rate[AXIS_PITCH]);
        float total_err = sqrtf(err_roll * err_roll + err_pitch * err_pitch);

        if (total_err > report->max_error_deg) {
            report->max_error_deg = total_err;
        }

        if (total_err > config->tracking_error_threshold_deg) {
            if (tracking_loss_start_time == 0) {
                tracking_loss_start_time = curr->timestamp_us;
            } else if (curr->timestamp_us - tracking_loss_start_time >= config->min_anomaly_duration_us) {
                report->flags |= ANOMALY_TRACKING_LOSS;
                if (!in_incident) {
                    report->start_time_us = tracking_loss_start_time;
                    in_incident = true;
                }
                report->end_time_us = curr->timestamp_us;
            }
        } else {
            tracking_loss_start_time = 0;
        }

        /* 3. Детектування десинхрону моторів у конфігурації Quad-X */
        float alpha_roll = (curr->gyro_rate[AXIS_ROLL] - prev->gyro_rate[AXIS_ROLL]) / dt;

        for (uint8_t m = 0; m < MAX_MOTORS; ++m) {
            if (curr->motor_output[m] >= config->desync_motor_min_throttle) {
                /* Перевірка протилежності реакції: тяга 100%, але кутове прискорення нульове або зворотне */
                bool opposing_accel = false;
                if (m == 3 && alpha_roll < -50.0f) opposing_accel = true; /* M4 має крен вліво замість вправо */
                if (m == 1 && alpha_roll > 50.0f)  opposing_accel = true; /* M2 крен вправо замість вліво */

                if (opposing_accel) {
                    if (desync_start_time[m] == 0) {
                        desync_start_time[m] = curr->timestamp_us;
                    } else if (curr->timestamp_us - desync_start_time[m] >= config->min_anomaly_duration_us) {
                        report->flags |= ANOMALY_MOTOR_DESYNC;
                        report->failed_motor_index = m;
                        if (!in_incident) {
                            report->start_time_us = desync_start_time[m];
                            in_incident = true;
                        }
                        report->end_time_us = curr->timestamp_us;
                    }
                }
            } else {
                desync_start_time[m] = 0;
            }
        }
    }

    return in_incident;
}
