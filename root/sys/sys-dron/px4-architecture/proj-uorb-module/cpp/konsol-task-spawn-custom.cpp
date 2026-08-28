int LoopWatch::task_spawn(int argc, char *argv[])
{
	LoopWatch *instance = new LoopWatch();

	if (instance) {
		_object.store(instance);
		_task_id = task_id_is_work_queue;   // «власного потоку немає, я на черзі»

		if (instance->init()) {
			return PX4_OK;
		}

	} else {
		PX4_ERR("alloc failed");
	}

	delete instance;
	_object.store(nullptr);
	_task_id = -1;

	return PX4_ERROR;
}

int LoopWatch::print_status()
{
	PX4_INFO("mean %u us, worst %u us, oldest sample %u us, gaps %u, missed %u",
		 (unsigned)(_wakeups ? _interval_sum / _wakeups : 0),
		 (unsigned)_interval_max, (unsigned)_sample_age_max,
		 (unsigned)_gaps, (unsigned)_missed);
	perf_print_counter(_cycle_perf);
	perf_print_counter(_interval_perf);
	perf_print_counter(_gap_perf);
	return 0;
}

int LoopWatch::custom_command(int argc, char *argv[])
{
	if (!is_running()) {
		PX4_ERR("not running");
		return 1;
	}

	if (argc > 0 && !strcmp(argv[0], "reset")) {
		get_instance()->_reset_request.store(true);   // прохання, а не дія
		return 0;
	}

	return print_usage("unknown command");
}

int LoopWatch::print_usage(const char *reason)
{
	if (reason) {
		PX4_WARN("%s\n", reason);
	}

	PRINT_MODULE_DESCRIPTION(
		R"DESCR_STR(
### Description
Watches the fast control loop from the consumer side. Runs on wq:rate_ctrl and is
scheduled by vehicle_angular_velocity publications, so its numbers are the numbers
the rate controller sees: wake-up interval, sample age and missed generations.
Publishes loop_health once per second.

### Examples
$ loop_watch start
$ loop_watch status
$ loop_watch reset
)DESCR_STR");

	PRINT_MODULE_USAGE_NAME("loop_watch", "system");
	PRINT_MODULE_USAGE_COMMAND("start");
	PRINT_MODULE_USAGE_COMMAND_DESCR("reset", "Clear the accumulated window");
	PRINT_MODULE_USAGE_DEFAULT_COMMANDS();

	return 0;
}

extern "C" __EXPORT int loop_watch_main(int argc, char *argv[])
{
	return LoopWatch::main(argc, argv);
}
