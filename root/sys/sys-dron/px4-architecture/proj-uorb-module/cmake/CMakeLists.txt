# src/modules/loop_watch/CMakeLists.txt
px4_add_module(
	MODULE modules__loop_watch
	MAIN loop_watch
	SRCS
		LoopWatch.cpp
		LoopWatch.hpp
	MODULE_CONFIG
		params.yaml
	DEPENDS
		px4_work_queue
	)
