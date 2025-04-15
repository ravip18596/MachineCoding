# Design Patterns

## Creational Design Patterns

1. Singleton
2. Factory
3. Builder

## Structural Design Patterns

## Behavioral Design Patterns

It deals with the action that needs to be performed

1. Strategy

### Singleton

Singleton is a design pattern that ensures that a class has only one instance, and provides a global point of access to it.

- For Single threaded applications

```java
public class Singleton {
    private static Singleton instance;
    private Singleton() {
    }
    public static Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }
}
```
- Python
```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

- For multithreaded applications
- Java

<b>Double-Checked Locking</b> - The outer  if (instance == null)check ensures that the synchronized block is only entered if the instance is not already created. This reduces the overhead of the lock once the instance is created.
```java
public class Singleton {
    private static Singleton instance;
    private static final Object lock = new Object();
    private Singleton() {
    }
    public static synchronized Singleton getInstance() {
        if (instance == null) {
            synchronized (lock) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```
- Python

```python
import threading

class Singleton:
    _instance = None
    _lock = threading.Lock()

    def getInstance(self):
        if Singleton._instance is None:
            with Singleton._lock:
                if Singleton._instance is None:
                    Singleton._instance = Singleton()
        return Singleton._instance
```

- Golang
```go
type Singleton struct {
    instance *Singleton
    sync.Mutex
}

func (s *Singleton) GetInstance() *Singleton {
    if s.instance == nil {
        s.Lock()
        defer s.Unlock()
        if s.instance == nil {
            s.instance = &Singleton{}
        }
    }
    return s.instance
}
```

### Strategy Design Pattern

A strategy design pattern is a behavioral design pattern that allows you to define a family of algorithms, encapsulate each one, and make them interchangeable.

```java
public class GoogleMaps {
    
}
```
