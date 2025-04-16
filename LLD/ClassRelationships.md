# Class Relationships

There are two type of class relationships among classes
1. IS-A (Inheritance)
2. HAS-A (Association)

## Inheritance (IS-A)

- Representation is <b>Parent Class <----- Child Class</b>

## Association (HAS-A)

- A class has a relationship with another class if it has a reference to the other class.
- Having another class as an attribute

1. Aggregation
   - weak association
   - contained entity can exist independently
   - <b>container class</b> < >----- <b>contained class</b>
   - example: Order < >----- Customer (Customer can exist without an Order)
2. Composition
   - strong association
   - contained entity cannot exist independently
   - <b>container class</b> <->----- <b>contained class</b>
   - example: Post <->----- Comment (Comment cannot exist without a Post)
