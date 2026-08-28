template <typename T>
struct DataHandler {
    void process() {
        // Незалежний виклик: не залежить від параметра типу T
        non_existent_function(42); 

        // Залежне ім'я типу: залежить від внутрішньої структури T
        typename T::iterator it; 
    }
};
