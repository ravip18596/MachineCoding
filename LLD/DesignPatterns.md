# Design Patterns

## Creational Design Patterns

- How will objects be created
- How many objects will be created

1. Singleton
2. Factory
3. Builder
4. Prototype

## Structural Design Patterns

- How will a class be structured
- What attributes/methods will be there
- How will a class interact with each another class

## Behavioral Design Patterns

- How to code an action

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

- When you search for a path in google maps, there are multiple ways of transport
- For different modes of transport, there are different ETA, route and suggestions
- Rather than implementing behaviours in a method, create a separate class for each behaviour
  - eg - CarPathCalculator, BikePathCalculator, WalkPathCalculator

![Class Diagram](GoogleMapsStrategyDesignPatternClassDiagram.drawio.png)

```java
public class GoogleMaps {
  public GoogleMaps(String mode, String src, String dest) {
    PathCalculator pathCalculator = PathCalculatorFactory.getPathCalculator(mode);
    pathCalculator.findPath(src, dest);
  }
  public static void main(String[] args) {

    GoogleMaps gm = new GoogleMaps("Car", "A", "B");
    GoogleMaps gm2 = new GoogleMaps("Bike", "A", "B");
    GoogleMaps gm3 = new GoogleMaps("Walk", "A", "B");
  }
}

public interface PathCalculator {
  public void findPath(String source, String destination);
}

public class BikePathCalculator implements PathCalculator {
  public void findPath(String source, String destination) {
    System.out.println("Bike path from " + source + " to " + destination);
  }
}

public class CarPathCalculator implements PathCalculator {
  public void findPath(String source, String destination) {
    System.out.println("Car path from " + source + " to " + destination);
  }
}

public class WalkPathCalculator implements PathCalculator {
  public void findPath(String source, String destination) {
    System.out.println("Walk path from " + source + " to " + destination);
  }
}

public class PathCalculatorFactory {
  public static PathCalculator getPathCalculator(String mode) {
    if (mode.equals("Car")) {
      return new CarPathCalculator();
    } else if (mode.equals("Bike")) {
      return new BikePathCalculator();
    } else if (mode.equals("Walk")) {
      return new WalkPathCalculator();
    }
    return null;
  }
}
```
