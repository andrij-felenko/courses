// src/modules/loop_watch/LoopWatch.cpp
#include "LoopWatch.hpp"

#include <cstring>

LoopWatch::LoopWatch() :
	ModuleParams(nullptr),
	ScheduledWorkItem(MODULE_NAME, px4::wq_configurations::rate_ctrl)
{
}

LoopWatch::~LoopWatch()
{
	perf_free(_cycle_perf);
	perf_free(_interval_perf);
	perf_free(_gap_perf);
}

bool LoopWatch::init()
{
	// прокидатися на кожній публікації vehicle_angular_velocity
	if (!_angular_velocity_sub.registerCallback()) {
		PX4_ERR("callback registration failed");
		return false;
	}

	resetWindow(hrt_absolute_time());

	// перше спрацювання запобіжника: якщо публікацій не буде взагалі,
	// нас має розбудити хоч щось — інакше ми мовчатимемо вічно
	ScheduleDelayed(BACKSTOP_US);
	return true;
}
