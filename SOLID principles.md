# SOLID Principles in Software Development

SOLID is an acronym for five design principles that improve maintainability, extensibility, and testability of object-oriented code.

## S — Single Responsibility Principle (SRP)
A class/module should have one, and only one, reason to change.
- Purpose: keep code focused and small.
- Violation: classes that mix business logic, persistence, and UI.
- Quick example (pseudo):
```java
class InvoicePrinter { void print(Invoice i) { ... } }   // separate from Invoice calculation
class Invoice { Money total() { ... } }
```

## O — Open/Closed Principle (OCP)
Software entities should be open for extension but closed for modification.
- Purpose: add behavior by extension (subclassing, composition, strategy) rather than changing existing code.
- Violation: modifying core classes for every new requirement.
- Pattern: use abstractions and plug-in implementations (Strategy, Decorator).

## L — Liskov Substitution Principle (LSP)
Subtypes must be substitutable for their base types without altering desirable properties.
- Purpose: preserve correctness when replacing base with derived types.
- Violation: overriding methods to throw or change expected behavior (e.g., a Square subclass breaking Rectangle contract).

## I — Interface Segregation Principle (ISP)
Clients should not be forced to depend on interfaces they do not use.
- Purpose: prefer many small, specific interfaces over one large fat interface.
- Violation: monolithic interfaces leading to empty/unimplemented methods on clients.
- Example: separate Readable and Writable interfaces instead of a combined ReadWrite.

## D — Dependency Inversion Principle (DIP)
High-level modules should not depend on low-level modules; both should depend on abstractions.
- Purpose: invert dependencies using interfaces or abstract classes and inject implementations (DI).
- Violation: high-level code instantiating low-level concrete classes directly.
- Typical approach: constructor injection of interfaces.

## Practical Tips
- Apply principles pragmatically — over-engineering is a risk.
- Start with SRP and DIP for immediate benefits in testability.
- Use automated tests to validate LSP when refactoring.
- Prefer composition over inheritance to satisfy OCP and keep changes localized.

References: these are general guidelines — adapt them to your language and project constraints.