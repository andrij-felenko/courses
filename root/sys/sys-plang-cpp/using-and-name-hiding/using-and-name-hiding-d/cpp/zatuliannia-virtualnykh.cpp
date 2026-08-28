struct BaseRenderer {
    virtual ~BaseRenderer() = default;
    virtual void render(int width, int height) = 0;
    virtual void render(double scale_factor) = 0;
};

struct SvgRenderer : public BaseRenderer {
    // Перевизначаємо лише один віртуальний метод:
    void render(int width, int height) override {
        std::cout << "SvgRenderer: " << width << "x" << height << '\n';
    }
    // render(double) з базового класу тепер ЗАТУЛЕНО для SvgRenderer
};

void run() {
    SvgRenderer svg;
    svg.render(800, 600); // ✓ Працює: точний збіг із SvgRenderer::render(int, int)
    
    // svg.render(1.5);   // ⚠ НЕ викликає render(double)! 
                          // 1.5 обрізається до int 1, викликаючи render(int, int) зі спотворенням!
    
    // Проте через покажчик на Base віртуальність працює повністю:
    BaseRenderer* base_ptr = &svg;
    // base_ptr->render(1.5); // Викличе чистий віртуальний метод Base (UB / runtime error), 
                              // бо SvgRenderer його не реалізував!
}
