# Multi-Scene State Management Guide

- **Single Source of Truth**: Store persistent run state (score, turn, level, inventory) in a dedicated state store or registry rather than inside UI text nodes.
- **Event Bus / Signals**: Decouple gameplay scenes from HUD/UI scenes using typed events (e.g., `score:updated`, `turn:changed`, `game:over`).
- **Clean Teardown**: Always unsubscribe from global event listeners when a scene shuts down or restarts.
