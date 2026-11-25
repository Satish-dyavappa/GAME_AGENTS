# Unreal Engine Rules & Best Practices

- Prefix UObject classes with `U`, Actors with `A`, and Structs with `F`.
- Use `UPROPERTY()` and `UFUNCTION()` macros for garbage collection safety and Blueprint exposure.
- Keep heavy per-frame logic out of `Tick()` when timers or event-driven delegates suffice.
