Chain of Responsibility
-----------------------

Chain of Responsibility is behavioral design pattern that allows passing request along the chain of potential handlers until one of them handles request.

client requests ----> | |handler1|--->|handler2|--->|handler3| |

the request goes from one handler to another till one of them satisfies the condition

[Read more ...](https://refactoring.guru/design-patterns/chain-of-responsibility/go/example#example-0)

Example LLD Problems on Chain of responsibility are - 

1. [Design Logger](Logger/logger.go)
2. Design ATM
3. Design Vending Machine
4. [Design Hospital App](Hospital/hospital.go)
