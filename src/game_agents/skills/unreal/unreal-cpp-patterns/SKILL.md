---
name: unreal-cpp-patterns
description: Unreal Engine 5 C++ best practices, UPROPERTY GC safety, delegates, and Tick optimization.
---

# Unreal Engine C++ Patterns Skill

1. **Reflection & GC Safety**:
   - Always mark `UObject*` member pointers with `UPROPERTY()` so Unreal's garbage collector tracks them.
   - Use `TObjectPtr<T>` in header files for UE5.
2. **Naming Conventions**:
   - `A` prefix for `AActor` subclasses, `U` for `UObject`/`UActorComponent`, `F` for structs, `E` for enums, `I` for interfaces.
3. **Avoid Unnecessary `Tick()`**:
   - Set `PrimaryActorTick.bCanEverTick = false;` when an actor can use timers (`FTimerHandle`) or event delegates instead.
