void run_full_pipeline_cpp(const std::vector<double>& signal) {
    try {
        takens::Embedder embedder(signal);
        auto embedding = embedder.auto_embed(); // Автоматичний вибір tau та m
        
        std::cout << "Успішно побудовано матрицю розміром " 
                  << embedding.rows() << " x " << embedding.cols() << "\n";
                  
        // Пам'ять звільняється автоматично у деструкторі embedding
    } catch (const std::exception& e) {
        std::cerr << "Помилка реконструкції: " << e.what() << "\n";
    }
}
