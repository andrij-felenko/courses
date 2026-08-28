// plan_flatten.cpp — .plan → список елементів місії, як його побачить борт.
// збірка: c++ -std=c++17 plan_flatten.cpp -o plan_flatten

#include <nlohmann/json.hpp>

#include <cmath>
#include <cstdio>
#include <fstream>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

using json = nlohmann::json;

constexpr int kNavWaypoint = 16;    // MAV_CMD_NAV_WAYPOINT
constexpr int kDoJump      = 177;   // MAV_CMD_DO_JUMP
constexpr int kFrameGlobal = 0;     // MAV_FRAME_GLOBAL — висота над рівнем моря

struct Item {
    int         seq      = 0;       // номер, якого у файлі немає: він обчислюється
    int         command  = 0;
    int         frame    = 0;
    bool        autoCont = true;
    double      p[7]     = {};
    std::string origin;             // звідки взявся елемент — лише для звіту
};

struct FlatMission {
    std::vector<Item>  items;
    std::map<int, int> seqOfJumpId;  // doJumpId → номер, лише прості елементи
};

// У JSON немає способу записати NaN, тому станція пише замість нього null.
// «Не задано» і «нуль» — різні накази: нуль у куті означає «дивитися на північ».
static double num(const json& value)
{
    return value.is_null() ? std::numeric_limits<double>::quiet_NaN()
                           : value.get<double>();
}

static Item itemFromJson(const json& object, std::string origin)
{
    const json& params = object.at("params");
    if (params.size() != 7) {
        throw std::runtime_error("елемент має " + std::to_string(params.size()) +
                                 " параметрів замість семи");
    }
    Item item;
    item.command  = object.at("command").get<int>();
    item.frame    = object.at("frame").get<int>();
    item.autoCont = object.value("autoContinue", true);
    for (int i = 0; i < 7; ++i) {
        item.p[i] = num(params[i]);
    }
    item.origin = std::move(origin);
    return item;
}

// Домашня точка: у файлі окремий ключ, на дроті — звичайний елемент у позиції 0.
static Item homeItem(const json& mission)
{
    const json& home = mission.at("plannedHomePosition");  // [широта, довгота, висота]
    Item item;
    item.command = kNavWaypoint;
    item.frame   = kFrameGlobal;
    item.p[4]    = num(home[0]);
    item.p[5]    = num(home[1]);
    item.p[6]    = num(home[2]);
    item.origin  = "plannedHomePosition";
    return item;
}

// Прохід перший — розгортання, прохід другий — нумерація.
static FlatMission flatten(const json& mission)
{
    FlatMission flat;
    flat.items.push_back(homeItem(mission));

    for (const json& object : mission.at("items")) {
        const std::string type = object.at("type").get<std::string>();

        if (type == "SimpleItem") {
            if (object.contains("doJumpId")) {
                // простий елемент займе рівно одну позицію — ту, що зараз наприкінці
                flat.seqOfJumpId[object["doJumpId"].get<int>()] =
                        static_cast<int>(flat.items.size());
            }
            flat.items.push_back(itemFromJson(object, "SimpleItem"));
        } else if (type == "ComplexItem") {
            const std::string kind = object.at("complexItemType").get<std::string>();
            const auto inner = object.find("TransectStyleComplexItem");
            if (inner == object.end() || !inner->contains("Items")) {
                throw std::runtime_error("складений елемент «" + kind +
                                         "» не тримає у файлі готових команд");
            }
            for (const json& sub : inner->at("Items")) {
                flat.items.push_back(itemFromJson(sub, kind));
            }
        } else {
            throw std::runtime_error("невідомий тип елемента: " + type);
        }
    }

    for (std::size_t i = 0; i < flat.items.size(); ++i) {
        flat.items[i].seq = static_cast<int>(i);
    }
    return flat;
}

// Прохід третій: тотожність → номер. Раніше його зробити не було з чого.
static void resolveJumps(FlatMission& flat)
{
    for (Item& item : flat.items) {
        if (item.command != kDoJump) {
            continue;
        }
        const int targetId = static_cast<int>(std::lround(item.p[0]));
        const auto found = flat.seqOfJumpId.find(targetId);
        if (found == flat.seqOfJumpId.end()) {
            throw std::runtime_error("DO_JUMP веде на doJumpId " + std::to_string(targetId) +
                                     ", якого в плані немає");
        }
        item.p[0] = found->second;
    }
}

// PX4 не бере домашньої точки в нульовій позиції, ArduPilot бере.
static void dropHome(std::vector<Item>& items)
{
    items.erase(items.begin());
    for (Item& item : items) {
        item.seq -= 1;
        if (item.command == kDoJump) {
            item.p[0] -= 1;
        }
    }
}

static const char* commandName(int command)
{
    switch (command) {
    case 16:  return "NAV_WAYPOINT";
    case 20:  return "NAV_RETURN_TO_LAUNCH";
    case 21:  return "NAV_LAND";
    case 22:  return "NAV_TAKEOFF";
    case 177: return "DO_JUMP";
    case 178: return "DO_CHANGE_SPEED";
    case 206: return "DO_SET_CAM_TRIGG_DIST";
    default:  return "?";
    }
}

static void show(const std::vector<Item>& items, const char* title)
{
    std::printf("%s\n", title);
    std::printf("seq  команда                frame     p1     широта    довгота  висота  джерело\n");
    for (const Item& item : items) {
        std::printf("%3d  %-22s %5d %6.0f  %9.4f  %9.4f  %6.1f  %s\n",
                    item.seq, commandName(item.command), item.frame,
                    item.p[0], item.p[4], item.p[5], item.p[6], item.origin.c_str());
    }
    std::printf("\n");
}

int main(int argc, char** argv)
{
    if (argc != 2) {
        std::fprintf(stderr, "вжиток: plan_flatten <файл.plan>\n");
        return 2;
    }
    try {
        std::ifstream file(argv[1]);
        if (!file) {
            throw std::runtime_error("файл не відкривається");
        }
        const json plan = json::parse(file);
        if (plan.value("fileType", std::string()) != "Plan") {
            throw std::runtime_error("це не файл плану");
        }

        FlatMission flat = flatten(plan.at("mission"));
        resolveJumps(flat);

        show(flat.items, "ArduPilot: домашня точка лишається номером 0");
        dropHome(flat.items);
        show(flat.items, "PX4: домашньої точки на дроті немає, решта зсунулася на одиницю");
    } catch (const std::exception& error) {
        std::fprintf(stderr, "план не розібрано: %s\n", error.what());
        return 1;
    }
    return 0;
}
