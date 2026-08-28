// Концепція виконання на GPU через stdexec
auto gpu_sch = gpu_context.get_scheduler();

auto pipeline = std::execution::schedule(cpu_pool.get_scheduler())
              | std::execution::then([] { return generate_input_matrix(); })
              | std::execution::continues_on(gpu_sch)
              | std::execution::then([](const Matrix& m) {
                    // Виконується на ядрах GPU (CUDA / Vulkan Compute)
                    return matrix_multiply_kernel(m);
                })
              | std::execution::continues_on(cpu_pool.get_scheduler())
              | std::execution::then([](const Matrix& res) {
                    save_result_to_disk(res);
                });
