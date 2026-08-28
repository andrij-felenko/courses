// fence_roundtrip.cpp — геозона з .plan → потік елементів → геозона назад.
// збірка: c++ -std=c++17 fence_roundtrip.cpp -o fence_roundtrip

#include <nlohmann/json.hpp>

#include <cmath>
#include <cstdio>
#include <fstream>
#include <string>
#include <vector>

using json = nlohmann::json;

constexpr int kFenceReturnPoint   = 5000;   // MAV_CMD_NAV_FENCE_RETURN_POINT
constexpr int kFenceVertexInclude = 5001;   // …POLYGON_VERTEX_INCLUSION
constexpr int kFenceVertexExclude = 5002;   // …POLYGON_VERTEX_EXCLUSION
constexpr int kFenceCircleInclude = 5003;   // …CIRCLE_INCLUSION
constexpr int kFenceCircleExclude = 5004;   // …CIRCLE_EXCLUSION

struct FenceItem {
    int    command = 0;
    double p1  = 0.0;    // у вершині — скільки вершин у фігурі; у колі — радіус
    double lat = 0.0;
    double lon = 0.0;
};

struct Vertex  { double lat = 0.0, lon = 0.0; };

struct Polygon {
    bool                inclusion = true;
    std::vector<Vertex> path;
};

struct Circle {
    bool   inclusion = true;
    double lat = 0.0, lon = 0.0, radius = 0.0;
};

struct Fence {
    std::vector<Polygon>     polygons;
    std::vector<Circle>      circles;
    bool                     hasReturnPoint = false;
    Vertex                   returnPoint;
    std::vector<std::string> complaints;
};

// Напрям «на борт»: фігури → плаский потік.
static std::vector<FenceItem> fenceToItems(const json& geoFence)
{
    std::vector<FenceItem> items;

    for (const json& polygon : geoFence.value("polygons", json::array())) {
        const json& path      = polygon.at("polygon");
        const bool  inclusion = polygon.at("inclusion").get<bool>();
        for (const json& vertex : path) {
            FenceItem item;
            item.command = inclusion ? kFenceVertexInclude : kFenceVertexExclude;
            item.p1  = static_cast<double>(path.size());  // єдине, що тримає фігуру купи
            item.lat = vertex[0].get<double>();
            item.lon = vertex[1].get<double>();
            items.push_back(item);
        }
    }
    for (const json& circle : geoFence.value("circles", json::array())) {
        const json& shape = circle.at("circle");
        FenceItem item;
        item.command = circle.at("inclusion").get<bool>() ? kFenceCircleInclude
                                                          : kFenceCircleExclude;
        item.p1  = shape.at("radius").get<double>();
        item.lat = shape.at("center")[0].get<double>();
        item.lon = shape.at("center")[1].get<double>();
        items.push_back(item);
    }
    return items;
}

// Напрям «з борту»: потік → фігури. Стан набору — три змінні на весь розбір.
static Fence itemsToFence(const std::vector<FenceItem>& items)
{
    Fence fence;
    std::vector<Vertex> pending;         // вершини фігури, яка ще набирається
    int expectedCount   = 0;
    int expectedCommand = 0;

    auto dropUnfinished = [&](const std::string& where) {
        if (!pending.empty()) {
            fence.complaints.push_back("недобраний полігон: " +
                                       std::to_string(pending.size()) + " вершин із " +
                                       std::to_string(expectedCount) + ", " + where);
            pending.clear();
        }
    };

    for (std::size_t i = 0; i < items.size(); ++i) {
        const FenceItem&  item = items[i];
        const std::string at   = "елемент " + std::to_string(i) + ": ";

        if (item.command == kFenceVertexInclude || item.command == kFenceVertexExclude) {
            const int count = static_cast<int>(std::lround(item.p1));

            if (pending.empty()) {
                expectedCount   = count;
                expectedCommand = item.command;
                if (expectedCount < 3) {
                    fence.complaints.push_back(at + "полігон із " +
                                               std::to_string(expectedCount) + " вершин");
                    continue;
                }
            } else if (count != expectedCount) {
                fence.complaints.push_back(at + "лічильник вершин змінився посеред полігону");
                pending.clear();
                continue;
            } else if (item.command != expectedCommand) {
                fence.complaints.push_back(at + "ґатунок полігону змінився, поки він набирався");
                pending.clear();
                continue;
            }

            pending.push_back(Vertex{item.lat, item.lon});
            if (static_cast<int>(pending.size()) == expectedCount) {
                Polygon polygon;
                polygon.inclusion = (expectedCommand == kFenceVertexInclude);
                polygon.path      = pending;
                fence.polygons.push_back(polygon);
                pending.clear();
            }
        } else if (item.command == kFenceCircleInclude || item.command == kFenceCircleExclude) {
            dropUnfinished("а далі вже коло");
            Circle circle;
            circle.inclusion = (item.command == kFenceCircleInclude);
            circle.lat       = item.lat;
            circle.lon       = item.lon;
            circle.radius    = item.p1;
            fence.circles.push_back(circle);
        } else if (item.command == kFenceReturnPoint) {
            dropUnfinished("а далі вже точка повернення");
            fence.hasReturnPoint = true;
            fence.returnPoint    = Vertex{item.lat, item.lon};
        } else {
            fence.complaints.push_back(at + "незнайома команда " +
                                       std::to_string(item.command));
            break;    // порядок — єдина структура; після незрозумілого елемента її вже немає
        }
    }
    dropUnfinished("а список уже скінчився");
    return fence;
}

static void report(const Fence& fence, const char* title)
{
    std::printf("%s\n", title);
    for (const Polygon& polygon : fence.polygons) {
        std::printf("  полігон %s, вершин %zu\n",
                    polygon.inclusion ? "включний" : "виключний", polygon.path.size());
    }
    for (const Circle& circle : fence.circles) {
        std::printf("  коло %s, радіус %.0f м, центр %.4f %.4f\n",
                    circle.inclusion ? "включне" : "виключне",
                    circle.radius, circle.lat, circle.lon);
    }
    if (fence.hasReturnPoint) {
        std::printf("  точка повернення %.4f %.4f\n",
                    fence.returnPoint.lat, fence.returnPoint.lon);
    }
    for (const std::string& complaint : fence.complaints) {
        std::printf("  ! %s\n", complaint.c_str());
    }
    std::printf("\n");
}

int main(int argc, char** argv)
{
    if (argc != 2) {
        std::fprintf(stderr, "вжиток: fence_roundtrip <файл.plan>\n");
        return 2;
    }
    std::ifstream file(argv[1]);
    if (!file) {
        std::fprintf(stderr, "файл не відкривається\n");
        return 1;
    }
    const json plan = json::parse(file);

    const std::vector<FenceItem> wire = fenceToItems(plan.at("geoFence"));
    std::printf("на дріт іде %zu елементів:\n", wire.size());
    for (const FenceItem& item : wire) {
        std::printf("  %4d  p1=%-6.1f %9.4f  %9.4f\n",
                    item.command, item.p1, item.lat, item.lon);
    }
    std::printf("\n");

    report(itemsToFence(wire), "зібралося назад:");

    if (wire.size() > 3) {
        std::vector<FenceItem> lossy = wire;   // хай один елемент не долетить
        lossy.erase(lossy.begin() + 3);
        report(itemsToFence(lossy), "той самий потік без однієї вершини:");
    }
    return 0;
}
