# Unity C# Rules & Best Practices

- Separate `Awake()` (self-initialization) from `Start()` (external references).
- Cache component references (`GetComponent<T>()`) in `Awake()` rather than calling them in `Update()`.
- Apply physics forces and velocity updates inside `FixedUpdate()`, not `Update()`.
- Never leave missing `.meta` files in `Assets/`.
