void LoopWatch::resetWindow(hrt_abstime now)
{
	_interval_sum = 0;
	_interval_max = 0;
	_sample_age_max = 0;
	_wakeups = 0;
	_gaps = 0;
	_missed = 0;
	_window_start = now;
}

void LoopWatch::publishHealth(hrt_abstime now)
{
	loop_health_s health{};

	health.interval_mean_us  = (_wakeups > 0) ? (uint32_t)(_interval_sum / _wakeups) : 0;
	health.interval_max_us   = _interval_max;
	health.sample_age_max_us = _sample_age_max;
	health.wakeups = _wakeups;
	health.gaps    = _gaps;
	health.missed  = _missed;
	health.armed   = _armed;

	const uint32_t int_limit = (uint32_t)_param_lw_int_max.get();
	const uint32_t age_limit = (uint32_t)_param_lw_age_max.get();

	if (_wakeups == 0) {
		health.state = loop_health_s::STATE_BROKEN;   // за ціле вікно жодної вибірки

	} else if ((_interval_max > int_limit) || (_sample_age_max > age_limit) || (_missed > 0)) {
		health.state = loop_health_s::STATE_DEGRADED;

	} else {
		health.state = loop_health_s::STATE_OK;
	}

	health.timestamp_sample = _last_run;            // на чому побудовано оцінку
	health.timestamp = hrt_absolute_time();         // коли її поклали на шину
	_loop_health_pub.publish(health);

	resetWindow(now);
	ScheduleDelayed(BACKSTOP_US);   // переставити запобіжник на наступні дві секунди
}
