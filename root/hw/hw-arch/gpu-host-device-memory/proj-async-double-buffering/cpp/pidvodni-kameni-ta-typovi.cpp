/* C++ ілюстрація помилкового фазового запуску */
for (size_t i = 0; i < num_chunks; ++i) {
    cudaMemcpyAsync(dev_in[i % 2].data(), host_in.data() + i * chunk_sz, 
                    chunk_sz * sizeof(float), cudaMemcpyHostToDevice, streams[i % 2].get());
}
for (size_t i = 0; i < num_chunks; ++i) {
    process_kernel<<<grid, block, 0, streams[i % 2].get()>>>(dev_in[i % 2].data(), dev_out[i % 2].data());
}
for (size_t i = 0; i < num_chunks; ++i) {
    cudaMemcpyAsync(host_out.data() + i * chunk_sz, dev_out[i % 2].data(), 
                    chunk_sz * sizeof(float), cudaMemcpyDeviceToHost, streams[i % 2].get());
}
