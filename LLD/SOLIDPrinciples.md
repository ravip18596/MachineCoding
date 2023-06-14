SOLID
-----

- S: Single Responsibility 
- O: Open/Closed
- L: Liskov Substitution
- I: Interface separation
- D: Dependency Inversion

## 1. Single Responsibility

A class should have one and only one reason to change,
meaning that a class should have only one job.

Initial -

```java
class Marker {
    String name;
    String color;
    int year;
    int price;

    public Marker(String name, String color, int year, int price) {
        this.name = name;
        this.color = color;
        this.year = year;
        this.price = price;
    }
}

class Invoice {
    Marker marker;
    int quantity;

    public Invoice(Marker marker, int quantity) {
        this.marker = marker;
        this.quantity = quantity;
    }

    public int calculateInvoice() {
        return marker.price * this.quantity;
    }

    public void printInvoice() {
        //print invoice
    }
    
    public void saveToDB() {
        // write to db
    }
}
```

Now break invoice class into classes having single responsibility

```java
class Marker {
    String name;
    String color;
    int year;
    int price;

    public Marker(String name, String color, int year, int price) {
        this.name = name;
        this.color = color;
        this.year = year;
        this.price = price;
    }
}

class Invoice {
    Marker marker;
    int quantity;

    public Invoice(Marker marker, int quantity) {
        this.marker = marker;
        this.quantity = quantity;
    }

    public int calculateInvoice() {
        return marker.price * this.quantity;
    }
}

class InvoicePrinter{
    private Invoice invoice;
    public InvoicePrinter(Invoice invoice) {
        this.invoice = invoice;
    }
    public void print() {
        
    }
}

class InvoiceDao {
    Invoice invoice;
    public InvoiceDao(Invoice invoice){
        this.invoice = invoice;
    }
    public void saveToDB() {
        // save to DB
    }
}
```

## 2. Open Closed Principle

Open-closed Principle (OCP) states:

    Objects or entities should be open for extension but closed for modification.

This means that a class should be extendable without modifying the class itself.
Don't modify an existing class, rather extends the class for new requirement.

Eg - If I want to save Invoice to a file, I will extend the InvoiceDao class 
rather than modifying the existing class

```java
interface InvoiceDao {
    public void save(Invoice invoice);
}

class DBInvoiceDao implements InvoiceDao{
    public void save(Invoice invoice){
        
    }
}

class FileInvoiceDao implements InvoiceDao{
    public void save(Invoice invoice){

    }
}
```

## 3. Liskov Substitution principle
Every subclass or derived class should be substitutable for their base or parent class.

```java

```

## 4. Interface segregation principle states:

A client should never be forced to implement an interface that it doesn’t use, or clients shouldn’t be forced to depend on methods they do not use.

Code not following interface segregation

- waiter doesn't cook and clean dishes, only serves customer.

```java
interface RestaurantEmployee {
    void cleanDishes();

    void cookFood();

    void serveCustomer();
}

class waiter implements RestaurantEmployee {
    @java.lang.Override
    public void cleanDishes() {

    }

    @java.lang.Override
    public void serveCustomer() {
        System.out.Println("Serving customer");
    }
}
```
 
- We will segregate RestaurantEmployee interface

```java
interface waiterInterface {
    void serveCustomer();
    void takeOrder();
}

interface ChefInterface {
    void cookFood();
    void decideMenu();
}
```

## 5. Dependency Inversion

Class should depend on interfaces rather than concrete class

Example of code that is directly dependent on concrete class
```java
interface Keyboard {
    
}
interface Mouse {
    
}

class WiredKeyboard implements Keyboard{
    
}
class BluetoothKeyboard implements Keyboard{
    
}
class WiredMouse implements Mouse{
    
}
class BluetoothMouse implements Mouse{
    
}
class Laptop {
    private final WiredKeyboard keyboard;
    private final WiredMouse mouse;
    public Laptop(){
        keyboard = new WiredKeyboard();
        mouse = new WiredMouse();
    }
}
```

instead Laptop should depend on interfaces

```java
class Laptop {
    private final Keyboard keyboard;
    private final Mouse mouse;
    public Laptop(Keyboard keyboard, Mouse mouse){
        this.keyboard = keyboard;
        this.mouse = mouse; 
    }
}
```