// C++26: std::function_ref не виділяє пам'ять і не копіює функтор
void process_events(std::function_ref<void(int)> callback) {
    callback(100);
}

int main() {
    auto heavy_lambda = [buffer = std::vector<int>(1000)] (int val) {
        // ...
    };
    
    // Передача без жодної алокації та без копіювання векторного буфера!
    process_events(heavy_lambda);
}
