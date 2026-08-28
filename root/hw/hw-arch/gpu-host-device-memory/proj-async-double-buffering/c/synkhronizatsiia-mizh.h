/* Координація потоків на GPU без блокування центрального процесора */
cudaEvent_t compute_ready;
cudaEventCreateWithFlags(&compute_ready, cudaEventDisableTiming);

/* Потік 0 завершує обчислення і записує подію в апаратний таймлайн */
kernel_stage1<<<grid, block, 0, stream0>>>(d_buf0);
cudaEventRecord(compute_ready, stream0);

/* Потік 1 починає залежну операцію ТІЛЬКИ після спрацювання події */
cudaStreamWaitEvent(stream1, compute_ready, 0);
kernel_stage2<<<grid, block, 0, stream1>>>(d_buf0, d_buf1);

/* CPU вільний і продовжує виконувати фонову логіку */
