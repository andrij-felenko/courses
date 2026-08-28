#include <iostream>
#include <vector>
#include <queue>
#include <memory>
#include <cmath>
#include <optional>
#include <algorithm>
#include <span>

constexpr double EPS = 1e-9;

struct Point {
    double x{0.0};
    double y{0.0};
};

struct VoronoiEdge {
    Point start{};
    Point end{};
    Point direction{};
    int site_left{-1};
    int site_right{-1};
    bool has_start{false};
    bool has_end{false};
};

enum class EventType { Site, Circle };

struct Arc;

struct Event {
    double y{0.0};
    Point point{};
    EventType type{EventType::Site};
    Arc* arc{nullptr};
    bool valid{true};
};

struct EventCompare {
    bool operator()(const std::shared_ptr<Event>& a, const std::shared_ptr<Event>& b) const noexcept {
        return a->y < b->y; // Максимальний Y обробляється першим
    }
};

struct Arc {
    Point site{};
    int site_idx{-1};
    Arc* prev{nullptr};
    Arc* next{nullptr};
    std::shared_ptr<Event> circle_event{nullptr};
    VoronoiEdge* edge_left{nullptr};
    VoronoiEdge* edge_right{nullptr};

    explicit Arc(Point s, int idx) : site(s), site_idx(idx) {}
};

class FortuneVoronoi {
public:
    explicit FortuneVoronoi(std::span<const Point> sites) : sites_(sites) {}

    std::vector<VoronoiEdge> build() {
        std::priority_queue<std::shared_ptr<Event>, 
                            std::vector<std::shared_ptr<Event>>, 
                            EventCompare> event_queue;

        for (int i = 0; i < static_cast<int>(sites_.size()); ++i) {
            auto ev = std::make_shared<Event>();
            ev->y = sites_[i].y;
            ev->point = sites_[i];
            ev->type = EventType::Site;
            ev->arc = nullptr;
            ev->valid = true;
            event_queue.push(std::move(ev));
        }

        Arc* root_arc = nullptr;

        while (!event_queue.empty()) {
            auto ev = event_queue.top();
            event_queue.pop();

            if (!ev->valid) continue;

            if (ev->type == EventType::Site) {
                handle_site_event(ev->point, root_arc, event_queue);
            } else {
                handle_circle_event(ev, root_arc, event_queue);
            }
        }

        clip_edges(Point{-1000.0, -1000.0}, Point{1000.0, 1000.0});
        return std::move(edges_);
    }

private:
    std::span<const Point> sites_;
    std::vector<VoronoiEdge> edges_;
    std::vector<std::unique_ptr<Arc>> arc_pool_;

    double get_breakpoint_x(Point p1, Point p2, double y_sweep) const noexcept {
        if (std::abs(p1.y - p2.y) < EPS) {
            return (p1.x + p2.x) / 2.0;
        }
        if (std::abs(p1.y - y_sweep) < EPS) return p1.x;
        if (std::abs(p2.y - y_sweep) < EPS) return p2.x;

        const double d1 = 1.0 / (2.0 * (p1.y - y_sweep));
        const double d2 = 1.0 / (2.0 * (p2.y - y_sweep));
        const double a = d1 - d2;
        const double b = 2.0 * (p2.x * d2 - p1.x * d1);
        const double c = (p1.x * p1.x + p1.y * p1.y - y_sweep * y_sweep) * d1 -
                         (p2.x * p2.x + p2.y * p2.y - y_sweep * y_sweep) * d2;

        const double discr = std::max(0.0, b * b - 4.0 * a * c);
        const double sq = std::sqrt(discr);

        const double x1 = (-b + sq) / (2.0 * a);
        const double x2 = (-b - sq) / (2.0 * a);

        return (p1.y < p2.y) ? std::max(x1, x2) : std::min(x1, x2);
    }

    std::optional<std::pair<Point, double>> get_circumcenter(Point a, Point b, Point c) const noexcept {
        const double d = 2.0 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y));
        if (d <= EPS) return std::nullopt;

        const double a2 = a.x * a.x + a.y * a.y;
        const double b2 = b.x * b.x + b.y * b.y;
        const double c2 = c.x * c.x + c.y * c.y;

        Point center{
            (a2 * (b.y - c.y) + b2 * (c.y - a.y) + c2 * (a.y - b.y)) / d,
            (a2 * (c.x - b.x) + b2 * (a.x - c.x) + c2 * (b.x - a.x)) / d
        };
        const double r = std::hypot(center.x - a.x, center.y - a.y);
        return std::make_pair(center, center.y - r);
    }

    void check_circle_event(Arc* arc, double y_sweep, auto& pq) {
        if (!arc || !arc->prev || !arc->next) return;

        if (auto res = get_circumcenter(arc->prev->site, arc->site, arc->next->site)) {
            const auto& [center, bottom_y] = *res;
            if (bottom_y <= y_sweep + EPS) {
                auto ev = std::make_shared<Event>();
                ev->y = bottom_y;
                ev->point = center;
                ev->type = EventType::Circle;
                ev->arc = arc;
                ev->valid = true;
                arc->circle_event = ev;
                pq.push(ev);
            }
        }
    }

    void handle_site_event(Point site, Arc*& root, auto& pq) {
        if (!root) {
            arc_pool_.push_back(std::make_unique<Arc>(site, 0));
            root = arc_pool_.back().get();
            return;
        }

        // Пошук дуги над новим сайтом
        Arc* curr = root;
        while (curr) {
            double left_x = curr->prev ? get_breakpoint_x(curr->prev->site, curr->site, site.y) : -1e9;
            double right_x = curr->next ? get_breakpoint_x(curr->site, curr->next->site, site.y) : 1e9;

            if (site.x >= left_x && site.x <= right_x) break;
            curr = curr->next;
        }
        if (!curr) curr = root;

        if (curr->circle_event) {
            curr->circle_event->valid = false;
            curr->circle_event = nullptr;
        }

        // Розщеплення дуги curr на curr -> new_arc -> right_arc
        arc_pool_.push_back(std::make_unique<Arc>(site, 0));
        Arc* middle = arc_pool_.back().get();

        arc_pool_.push_back(std::make_unique<Arc>(curr->site, curr->site_idx));
        Arc* right = arc_pool_.back().get();

        right->next = curr->next;
        if (right->next) right->next->prev = right;
        right->prev = middle;
        middle->next = right;
        middle->prev = curr;
        curr->next = middle;

        edges_.push_back(VoronoiEdge{
            .direction = Point{-(site.y - curr->site.y), site.x - curr->site.x},
            .site_left = curr->site_idx,
            .site_right = 0
        });
        VoronoiEdge* e = &edges_.back();

        curr->edge_right = e;
        middle->edge_left = e;
        middle->edge_right = e;
        right->edge_left = e;

        check_circle_event(curr, site.y, pq);
        check_circle_event(right, site.y, pq);
    }

    void handle_circle_event(const std::shared_ptr<Event>& ev, Arc*& root, auto& pq) {
        Arc* arc = ev->arc;
        Point vertex = ev->point;

        if (arc->edge_left) {
            arc->edge_left->end = vertex;
            arc->edge_left->has_end = true;
        }
        if (arc->edge_right) {
            arc->edge_right->start = vertex;
            arc->edge_right->has_start = true;
        }

        edges_.push_back(VoronoiEdge{
            .start = vertex,
            .direction = Point{-(arc->next->site.y - arc->prev->site.y), 
                               arc->next->site.x - arc->prev->site.x},
            .has_start = true
        });
        VoronoiEdge* new_edge = &edges_.back();

        if (arc->prev) {
            arc->prev->next = arc->next;
            arc->prev->edge_right = new_edge;
        }
        if (arc->next) {
            arc->next->prev = arc->prev;
            arc->next->edge_left = new_edge;
        }
        if (arc == root) root = arc->next ? arc->next : arc->prev;

        if (arc->prev) check_circle_event(arc->prev, ev->y, pq);
        if (arc->next) check_circle_event(arc->next, ev->y, pq);
    }

    void clip_edges(Point min_box, Point max_box) noexcept {
        for (auto& edge : edges_) {
            if (!edge.has_start && !edge.has_end) {
                edge.start = Point{min_box.x, min_box.y};
                edge.end = Point{max_box.x, max_box.y};
            } else if (edge.has_start && !edge.has_end) {
                edge.end = Point{
                    edge.start.x + edge.direction.x * 2000.0,
                    edge.start.y + edge.direction.y * 2000.0
                };
            }
        }
    }
};
