/* ПОМИЛКА: фазове групування руйнує асинхронний конвеєр */
for (int i = 0; i < N; ++i) {
    cudaMemcpyAsync(d_in[i % 2], h_in + i * S, S * sizeof(float), cudaMemcpyHostToDevice, streams[i % 2]);
}
for (int i = 0; i < N; ++i) {
    kernel<<<grid, block, 0, streams[i % 2]>>>(d_in[i % 2], d_out[i % 2]);
}
for (int i = 0; i < N; ++i) {
    cudaMemcpyAsync(h_out + i * S, d_out[i % 2], S * sizeof(float), cudaMemcpyDeviceToHost, streams[i % 2]);
}
