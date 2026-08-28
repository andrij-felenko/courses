void LoopWatch::Run()
{
	if (should_exit()) {
		_angular_velocity_sub.unregisterCallback();
		ScheduleClear();      // зняти відкладений виклик, бо об'єкт зараз помре
		exit_and_cleanup();
		return;
	}

	perf_begin(_cycle_perf);
	perf_count(_interval_perf);

	const hrt_abstime now = hrt_absolute_time();

	if (_reset_request.load()) {
		_reset_request.store(false);
		resetWindow(now);
	}

	// параметри: підписка сама обмежує себе однією перевіркою на секунду
	if (_parameter_update_sub.updated()) {
		parameter_update_s pupdate;
		_parameter_update_sub.copy(&pupdate);   // прибрати позначку оновлення
		updateParams();                         // перечитати LW_INT_MAX і LW_AGE_MAX
	}

	vehicle_status_s status;

	if (_vehicle_status_sub.update(&status)) {
		_armed = (status.arming_state == vehicle_status_s::ARMING_STATE_ARMED);
	}

	vehicle_angular_velocity_s av;

	if (_angular_velocity_sub.update(&av)) {
		const unsigned generation = _angular_velocity_sub.get_last_generation();

		if (_primed) {
			// у здоровому випадку покоління зростає рівно на одиницю
			const unsigned step = generation - _last_generation;

			if (step > 1) {
				_gaps++;
				_missed += step - 1;
				perf_count(_gap_perf);
			}

			const uint32_t interval = now - _last_run;
			_interval_sum += interval;
			_wakeups++;

			if (interval > _interval_max) {
				_interval_max = interval;
			}
		}

		const uint32_t age = now - av.timestamp_sample;

		if (age > _sample_age_max) {
			_sample_age_max = age;
		}

		_last_generation = generation;
		_last_run = now;
		_primed = true;
	}

	if (now - _window_start >= WINDOW_US) {
		publishHealth(now);
	}

	perf_end(_cycle_perf);
}
