struct Base {
    int counter;
};

struct Left : public Base {
    void stepLeft() { counter++; }
};

struct Right : public Base {
    void stepRight() { counter += 2; }
};

struct Bottom : public Left, public Right {
    void stepBoth() {
        // counter++; // ПОМИЛКА КОМПІЛЯЦІЇ: неоднозначність!
        Left::counter++;   // змінює копію Base всередині Left
        Right::counter++;  // змінює копію Base всередині Right
    }
};
