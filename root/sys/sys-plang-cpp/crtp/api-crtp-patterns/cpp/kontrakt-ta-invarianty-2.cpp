template <typename Derived>
class EventPipeline {
public:
    void process_event() {
        Derived& self = *static_cast<Derived*>(this);
        
        // Перевірка наявності опційного метода під час компіляції
        if constexpr (requires { self.before_process(); }) {
            self.before_process();
        }
        
        self.main_process();
        
        if constexpr (requires { self.after_process(); }) {
            self.after_process();
        }
    }
};

class SimpleHandler : public EventPipeline<SimpleHandler> {
public:
    void main_process() {
        std::cout << "Executing main event handler\n";
    }
};
