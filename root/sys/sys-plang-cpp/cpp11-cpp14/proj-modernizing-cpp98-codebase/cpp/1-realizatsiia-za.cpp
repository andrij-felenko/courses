#include <pthread.h>
#include <queue>
#include <vector>
#include <string>
#include <iostream>

// 1. Абстрактний інтерфейс завдання в об'єктно-орієнтованому стилі C++98
class ITask {
public:
    virtual ~ITask() {}
    virtual void execute() = 0;
};

// 2. Конкретна реалізація обробника мережевого пакета
class PacketProcessTask : public ITask {
private:
    std::string       m_tag;
    std::vector<char> m_payload; // Глибока копія даних у купі!

public:
    PacketProcessTask(const std::string& tag, const std::vector<char>& payload)
        : m_tag(tag), m_payload(payload) {} // Виклик копіювальних конструкторів

    virtual void execute() {
        std::cout << "Обробка пакета [" << m_tag << "], розмір: " 
                  << m_payload.size() << " байтів\n";
    }
};

// 3. Потокобезпечна черга завдань на базі примітивів pthread
class Cxx98TaskQueue {
private:
    std::queue<ITask*> m_queue; // Небезпека: сирі покажчики на динамічну пам'ять
    pthread_mutex_t    m_mutex;
    pthread_cond_t     m_cond;
    bool               m_shutdown;

    // Заборона копіювання за стандартом C++98: приватні оголошення без тіла
    Cxx98TaskQueue(const Cxx98TaskQueue&);
    Cxx98TaskQueue& operator=(const Cxx98TaskQueue&);

public:
    Cxx98TaskQueue() : m_shutdown(false) {
        pthread_mutex_init(&m_mutex, NULL);
        pthread_cond_init(&m_cond, NULL);
    }

    ~Cxx98TaskQueue() {
        stop();
        // Ручне звільнення залишків черги для уникнення витоку пам'яті
        pthread_mutex_lock(&m_mutex);
        while (!m_queue.empty()) {
            ITask* task = m_queue.front();
            m_queue.pop();
            delete task;
        }
        pthread_mutex_unlock(&m_mutex);
        pthread_mutex_destroy(&m_mutex);
        pthread_cond_destroy(&m_cond);
    }

    void push(ITask* task) {
        pthread_mutex_lock(&m_mutex);
        m_queue.push(task);
        pthread_cond_signal(&m_cond);
        pthread_mutex_unlock(&m_mutex);
    }

    ITask* pop() {
        pthread_mutex_lock(&m_mutex);
        // Цикл захисту від хибного пробудження (Spurious Wakeup)
        while (m_queue.empty() && !m_shutdown) {
            pthread_cond_wait(&m_cond, &m_mutex);
        }
        if (m_shutdown && m_queue.empty()) {
            pthread_mutex_unlock(&m_mutex);
            return NULL;
        }
        ITask* task = m_queue.front();
        m_queue.pop();
        pthread_mutex_unlock(&m_mutex);
        return task; // Відповідальність за delete перекладається на клієнта!
    }

    void stop() {
        pthread_mutex_lock(&m_mutex);
        m_shutdown = true;
        pthread_cond_broadcast(&m_cond);
        pthread_mutex_unlock(&m_mutex);
    }
};
