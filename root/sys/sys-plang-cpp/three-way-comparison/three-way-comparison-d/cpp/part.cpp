struct Point {
    int x;
    int y;

    bool operator==(const Point& o) const { return x == o.x && y == o.y; }
    bool operator!=(const Point& o) const { return !(*this == o); }
    bool operator< (const Point& o) const { return x < o.x || (x == o.x && y < o.y); }
    bool operator<=(const Point& o) const { return !(o < *this); }
    bool operator> (const Point& o) const { return o < *this; }
    bool operator>=(const Point& o) const { return !(*this < o); }
};
