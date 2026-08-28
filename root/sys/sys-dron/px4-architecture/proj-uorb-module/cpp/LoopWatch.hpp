// src/modules/loop_watch/LoopWatch.hpp
#pragma once

#include <px4_platform_common/atomic.h>
#include <px4_platform_common/defines.h>
#include <px4_platform_common/module.h>
#include <px4_platform_common/module_params.h>
#include <px4_platform_common/posix.h>
#include <px4_platform_common/px4_work_queue/ScheduledWorkItem.hpp>

#include <drivers/drv_hrt.h>
#include <lib/perf/perf_counter.h>

#include <uORB/Publication.hpp>
#include <uORB/Subscription.hpp>
#include <uORB/SubscriptionCallback.hpp>
#include <uORB/topics/loop_health.h>
#include <uORB/topics/parameter_update.h>
#include <uORB/topics/vehicle_angular_velocity.h>
#include <uORB/topics/vehicle_status.h>

using namespace time_literals;

class LoopWatch : public ModuleBase<LoopWatch>, public ModuleParams, public px4::ScheduledWorkItem
{
public:
	LoopWatch();
	~LoopWatch() override;

	/** @see ModuleBase */
	static int task_spawn(int argc, char *argv[]);
	static int custom_command(int argc, char *argv[]);
	static int print_usage(const char *reason = nullptr);

	bool init();
	int print_status() override;

private:
	void Run() override;
	void publishHealth(hrt_abstime now);
	void resetWindow(hrt_abstime now);

	static constexpr uint32_t WINDOW_US   = 1000000;      // вікно спостереження — 1 с
	static constexpr uint32_t BACKSTOP_US = 2 * WINDOW_US; // запобіжник, якщо публікації спиняться

	// Публікації
	uORB::Publication<loop_health_s> _loop_health_pub{ORB_ID(loop_health)};

	// Підписки
	uORB::SubscriptionCallbackWorkItem _angular_velocity_sub{this, ORB_ID(vehicle_angular_velocity)};
	uORB::SubscriptionInterval         _parameter_update_sub{ORB_ID(parameter_update), 1_s};
	uORB::Subscription                 _vehicle_status_sub{ORB_ID(vehicle_status)};

	// Лічильники продуктивності
	perf_counter_t _cycle_perf{perf_alloc(PC_ELAPSED, MODULE_NAME": cycle")};
	perf_counter_t _interval_perf{perf_alloc(PC_INTERVAL, MODULE_NAME": interval")};
	perf_counter_t _gap_perf{perf_alloc(PC_COUNT, MODULE_NAME": generation gap")};

	// Накопичувачі вікна
	hrt_abstime _last_run{0};
	hrt_abstime _window_start{0};
	unsigned    _last_generation{0};
	bool        _primed{false};

	uint64_t _interval_sum{0};
	uint32_t _interval_max{0};
	uint32_t _sample_age_max{0};
	uint32_t _wakeups{0};
	uint32_t _gaps{0};
	uint32_t _missed{0};
	bool     _armed{false};

	px4::atomic<bool> _reset_request{false};

	DEFINE_PARAMETERS(
		(ParamInt<px4::params::LW_INT_MAX>) _param_lw_int_max,
		(ParamInt<px4::params::LW_AGE_MAX>) _param_lw_age_max
	)
};
