struct Widget {
    ~Widget() {
        try {
            // Внутрішня безаварійна операція
            do_internal_work(); 
        } catch (...) {
            // локально перехопили внутрішню помилку
        }
    }
};
