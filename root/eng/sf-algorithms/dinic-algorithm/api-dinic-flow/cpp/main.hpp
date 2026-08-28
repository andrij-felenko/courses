#ifndef DINIC_FLOW_HPP
#define DINIC_FLOW_HPP

#include <cstdint>
#include <vector>
#include <limits>
#include <string>
#include <stdexcept>

namespace flow {

enum class Status {
    Success = 0,
    InvalidVertex = 1,
    NegativeCapacity = 2,
    SameSourceSink = 3,
    UnconnectedGraph = 4,
    OverflowDetected = 5
};

template <typename FlowType = int64_t>
struct FlowEdge {
    int32_t from;
    int32_t to;
    FlowType capacity;
    FlowType flow;
    uint32_t id;

    FlowType residual_capacity() const { return capacity - flow; }
    bool is_saturated() const { return flow >= capacity; }
};

template <typename FlowType = int64_t>
struct CutResult {
    std::vector<bool> in_source_set;
    FlowType cut_capacity;
    std::vector<uint32_t> cut_edge_ids;
};

template <typename FlowType = int64_t>
class IDinicFlow {
public:
    virtual ~IDinicFlow() = default;

    // Додавання орієнтованого ребра from -> to.
    // Повертає унікальний ідентифікатор доданого ребра.
    virtual uint32_t add_edge(int32_t from, int32_t to, FlowType cap, FlowType rev_cap = 0) = 0;

    // Обчислення максимального потоку від source до sink
    virtual FlowType solve(int32_t source, int32_t sink) = 0;

    // Обчислення максимального потоку з масштабуванням місткостей
    virtual FlowType solve_scaled(int32_t source, int32_t sink, FlowType min_delta = 1) = 0;

    // Отримання поточного потоку через ребро за його ідентифікатором
    virtual FlowType get_flow(uint32_t edge_id) const = 0;

    // Отримання повної інформації про ребро
    virtual FlowEdge<FlowType> get_edge_info(uint32_t edge_id) const = 0;

    // Виділення мінімального розрізу
    virtual CutResult<FlowType> extract_min_cut(int32_t source) const = 0;

    // Зміна місткості ребра без повної перебудови графа
    virtual void update_capacity(uint32_t edge_id, FlowType new_capacity) = 0;

    // Скидання всіх потоків до нуля для повторного обчислення
    virtual void reset_flow() = 0;

    // Повне очищення графа
    virtual void clear() = 0;

    // Експорт графа у формат DIMACS
    virtual std::string export_dimacs(int32_t source, int32_t sink) const = 0;
};

} // namespace flow

#endif // DINIC_FLOW_HPP
