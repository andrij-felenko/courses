/* C: захоплення та створення виконуваного графа */
cudaGraph_t graph;
cudaGraphExec_t instance;

cudaStreamBeginCapture(stream, cudaStreamCaptureModeGlobal);
/* Виклики асинхронного конвеєра записуються в граф без виконання */
cudaMemcpyAsync(d_in, h_in, size, cudaMemcpyHostToDevice, stream);
process_kernel<<<grid, block, 0, stream>>>(d_in, d_out, 1.0f, n);
cudaMemcpyAsync(h_out, d_out, size, cudaMemcpyDeviceToHost, stream);
cudaStreamEndCapture(stream, &graph);

/* Інстанціювання оптимізованого графа */
cudaGraphInstantiate(&instance, graph, NULL, NULL, 0);

/* Багаторазовий миттєвий запуск без участі драйвера CPU */
for (int frame = 0; frame < 10000; ++frame) {
    cudaGraphLaunch(instance, stream);
}
