#ifndef BALANCE_ATOMIC_H
#define BALANCE_ATOMIC_H

#include <unistd.h>

#include <mutex>
#include <queue>

namespace balance {
namespace util {

template<class T>
class AtomicQueue;

template<class T>
class AtomicQueue {
public:
    AtomicQueue() {}
    AtomicQueue(const AtomicQueue<T> &aq): _q(aq._q) {}
    AtomicQueue<T> operator=(const AtomicQueue<T> &aq) {return AtomicQueue(aq);}
    ~AtomicQueue() {}
    
    bool empty() {
        const std::lock_guard<std::mutex> guard(_lock);
        return _q.empty();
    }

    void push(T t) {
        const std::lock_guard<std::mutex> guard(_lock);
        _q.push(t);
    }

    T pop() {
        const std::lock_guard<std::mutex> guard(_lock);
        T t = _q.front();
        _q.pop();
        return t;
    }

private:
    std::queue<T> _q;
    std::mutex _lock;
};


} //namespace util
} //namespace balance

#endif