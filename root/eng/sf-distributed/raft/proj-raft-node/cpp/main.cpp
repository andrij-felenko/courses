#include <iostream>
#include <vector>
#include <optional>
#include <cstdint>
#include <algorithm>
#include <chrono>

enum class Role {
    Follower,
    Candidate,
    Leader
};

struct LogEntry {
    uint64_t term{0};
    uint64_t index{0};
    int32_t  data{0};
};

struct RequestVoteArgs {
    uint64_t term{0};
    uint32_t candidateId{0};
    uint64_t lastLogIndex{0};
    uint64_t lastLogTerm{0};
};

struct RequestVoteReply {
    uint64_t term{0};
    bool     voteGranted{false};
};

struct AppendEntriesArgs {
    uint64_t term{0};
    uint32_t leaderId{0};
    uint64_t prevLogIndex{0};
    uint64_t prevLogTerm{0};
    uint64_t leaderCommit{0};
    std::vector<LogEntry> entries;
};

struct AppendEntriesReply {
    uint64_t term{0};
    bool     success{false};
    uint64_t matchIndex{0};
    uint64_t conflictTerm{0};
    uint64_t conflictFirstIndex{0};
};

class RaftNode {
public:
    RaftNode(uint32_t id, uint32_t clusterSize)
        : m_id(id), m_clusterSize(clusterSize) {
        m_nextIndex.resize(clusterSize, 1);
        m_matchIndex.resize(clusterSize, 0);
    }

    void startElection() {
        m_role = Role::Candidate;
        m_currentTerm++;
        m_votedFor = m_id;
        m_votesReceived = 1;

        std::cout << "[Вузол " << m_id << "] Став Кандидатом, новий Терм "
                  << m_currentTerm << ", розсилка RequestVote\n";
    }

    RequestVoteReply handleRequestVote(const RequestVoteArgs& args) {
        if (args.term > m_currentTerm) {
            m_currentTerm = args.term;
            m_role = Role::Follower;
            m_votedFor.reset();
        }

        RequestVoteReply reply{.term = m_currentTerm, .voteGranted = false};
        if (args.term < m_currentTerm) {
            return reply;
        }

        bool canVote = (!m_votedFor.has_value() || *m_votedFor == args.candidateId);
        if (!canVote) return reply;

        uint64_t myLastTerm = getLastLogTerm();
        uint64_t myLastIdx  = getLastLogIndex();

        bool logIsUpToDate = (args.lastLogTerm > myLastTerm) ||
                             (args.lastLogTerm == myLastTerm && args.lastLogIndex >= myLastIdx);

        if (logIsUpToDate) {
            m_votedFor = args.candidateId;
            reply.voteGranted = true;
            std::cout << "[Вузол " << m_id << "] Віддав голос за кандидата "
                      << args.candidateId << " у термі " << m_currentTerm << "\n";
        }
        return reply;
    }

    AppendEntriesReply handleAppendEntries(const AppendEntriesArgs& args) {
        if (args.term > m_currentTerm) {
            m_currentTerm = args.term;
            m_role = Role::Follower;
            m_votedFor.reset();
        }

        AppendEntriesReply reply{
            .term = m_currentTerm,
            .success = false,
            .matchIndex = m_log.size(),
            .conflictTerm = 0,
            .conflictFirstIndex = 0
        };

        if (args.term < m_currentTerm) {
            return reply;
        }

        if (m_role == Role::Candidate) {
            m_role = Role::Follower;
        }

        /* Перевірка інваріанта відповідності (Log Matching) */
        if (args.prevLogIndex > 0) {
            if (args.prevLogIndex > m_log.size()) {
                reply.conflictFirstIndex = m_log.size() + 1;
                return reply;
            }
            if (m_log[args.prevLogIndex - 1].term != args.prevLogTerm) {
                uint64_t cTerm = m_log[args.prevLogIndex - 1].term;
                reply.conflictTerm = cTerm;
                uint64_t firstIdx = args.prevLogIndex;
                while (firstIdx > 1 && m_log[firstIdx - 2].term == cTerm) {
                    firstIdx--;
                }
                reply.conflictFirstIndex = firstIdx;
                m_log.resize(args.prevLogIndex - 1);
                return reply;
            }
        }

        /* Дописування або перезапис конфліктних записів */
        for (size_t i = 0; i < args.entries.size(); ++i) {
            size_t insertIdx = args.prevLogIndex + 1 + i;
            if (insertIdx <= m_log.size()) {
                if (m_log[insertIdx - 1].term != args.entries[i].term) {
                    m_log.resize(insertIdx - 1);
                    m_log.push_back(args.entries[i]);
                }
            } else {
                m_log.push_back(args.entries[i]);
            }
        }

        /* Оновлення commitIndex за вказівкою лідера */
        if (args.leaderCommit > m_commitIndex) {
            m_commitIndex = std::min(args.leaderCommit, static_cast<uint64_t>(m_log.size()));
        }

        reply.success = true;
        reply.matchIndex = m_log.size();
        return reply;
    }

    void advanceLeaderCommit() {
        if (m_role != Role::Leader) return;

        for (uint64_t n = m_log.size(); n > m_commitIndex; --n) {
            /* Тільки записи поточного терму фіксуються напряму! (§5.4.2) */
            if (m_log[n - 1].term != m_currentTerm) {
                continue;
            }

            uint32_t matchCount = 1;
            for (uint32_t peer = 0; peer < m_clusterSize; ++peer) {
                if (peer != m_id && m_matchIndex[peer] >= n) {
                    matchCount++;
                }
            }

            if (matchCount > m_clusterSize / 2) {
                m_commitIndex = n;
                std::cout << "[Лідер " << m_id << "] Просунув commitIndex до "
                          << m_commitIndex << " у термі " << m_currentTerm << "\n";
                break;
            }
        }
    }

    [[nodiscard]] uint64_t getLastLogTerm() const {
        return m_log.empty() ? 0 : m_log.back().term;
    }

    [[nodiscard]] uint64_t getLastLogIndex() const {
        return m_log.size();
    }

    [[nodiscard]] Role getRole() const { return m_role; }
    [[nodiscard]] uint64_t getCurrentTerm() const { return m_currentTerm; }
    [[nodiscard]] uint64_t getCommitIndex() const { return m_commitIndex; }

private:
    uint32_t                m_id;
    uint32_t                m_clusterSize;
    Role                    m_role{Role::Follower};

    uint64_t                m_currentTerm{0};
    std::optional<uint32_t> m_votedFor{std::nullopt};
    std::vector<LogEntry>   m_log;

    uint64_t                m_commitIndex{0};
    uint64_t                m_lastApplied{0};

    std::vector<uint64_t>   m_nextIndex;
    std::vector<uint64_t>   m_matchIndex;
    uint32_t                m_votesReceived{0};
};
