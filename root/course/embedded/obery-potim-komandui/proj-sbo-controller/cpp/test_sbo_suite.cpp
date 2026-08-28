// test_sbo_suite.cpp — Модульні тести на базі C++20
#include <cassert>
#include <iostream>

void run_cpp_sbo_tests() {
    using namespace std::chrono_literals;
    sbo::TargetEngine target{sbo::NodeId{0x02}};
    auto now = std::chrono::steady_clock::now();

    // Тест 1: Пряме виконання без селекції
    sbo::Packet direct_op{};
    direct_op.target = sbo::NodeId{0x02};
    direct_op.source = sbo::NodeId{0xFE};
    direct_op.type = sbo::MessageType::OperateReq;
    direct_op.command = sbo::CommandCode{0x0101};
    direct_op.token = sbo::Token{0x11223344};

    auto res = target.process_packet(direct_op, now);
    assert(res.has_value());
    assert(res->type == sbo::MessageType::OperateNack);
    assert(target.state() == sbo::State::Idle);

    // Тест 2: Номінальна селекція
    sbo::Packet select_pkt{};
    select_pkt.target = sbo::NodeId{0x02};
    select_pkt.source = sbo::NodeId{0xFE};
    select_pkt.type = sbo::MessageType::SelectReq;
    select_pkt.command = sbo::CommandCode{0x0101};
    select_pkt.timeout = 5000ms;

    auto sel_res = target.process_packet(select_pkt, now);
    assert(sel_res.has_value());
    assert(sel_res->type == sbo::MessageType::SelectAck);
    assert(target.state() == sbo::State::Armed);
    auto token = sel_res->token;

    // Тест 3: Виконання після тайм-ауту (+6 секунд)
    auto future_time = now + 6000ms;
    sbo::Packet op_late{};
    op_late.target = sbo::NodeId{0x02};
    op_late.source = sbo::NodeId{0xFE};
    op_late.type = sbo::MessageType::OperateReq;
    op_late.command = sbo::CommandCode{0x0101};
    op_late.token = token;

    auto late_res = target.process_packet(op_late, future_time);
    assert(late_res.has_value());
    assert(late_res->type == sbo::MessageType::OperateNack);
    assert(target.state() == sbo::State::Idle);
}
