struct Base {
    int counter;
};

struct Left : virtual public Base {
    int left_data;
};

struct Right : virtual public Base {
    int right_data;
};

struct Bottom : public Left, public Right {
    int bot_data;
};
