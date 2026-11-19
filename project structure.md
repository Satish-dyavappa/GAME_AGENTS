
game-dev-agents/
│
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── README.md
├── CONTRIBUTING.md
│
├── config/
│   ├── app.yaml
│   ├── models.yaml
│   ├── agents.yaml
│   ├── engines.yaml
│   ├── permissions.yaml
│   └── logging.yaml
│
├── src/
│   └── game_dev_agents/
│       │
│       ├── __init__.py
│       │
│       ├── core/
│       │   ├── runtime/
│       │   │   ├── orchestrator.py
│       │   │   ├── agent_registry.py
│       │   │   ├── agent_factory.py
│       │   │   └── execution_manager.py
│       │   │
│       │   ├── routing/
│       │   │   ├── intent_router.py
│       │   │   ├── engine_router.py
│       │   │   ├── task_router.py
│       │   │   └── model_router.py
│       │   │
│       │   ├── state/
│       │   │   ├── agent_state.py
│       │   │   ├── project_state.py
│       │   │   ├── task_state.py
│       │   │   └── execution_state.py
│       │   │
│       │   ├── context/
│       │   │   ├── context_builder.py
│       │   │   ├── project_context.py
│       │   │   ├── code_context.py
│       │   │   └── context_selector.py
│       │   │
│       │   ├── memory/
│       │   │   ├── short_term.py
│       │   │   ├── long_term.py
│       │   │   ├── episodic.py
│       │   │   └── memory_manager.py
│       │   │
│       │   └── contracts/
│       │       ├── task.py
│       │       ├── agent_result.py
│       │       ├── tool_result.py
│       │       └── project_manifest.py
│       │
│       ├── agents/
│       │   ├── base/
│       │   │   ├── base_agent.py
│       │   │   └── agent_config.py
│       │   │
│       │   ├── orchestration/
│       │   │   ├── supervisor.py
│       │   │   ├── planner.py
│       │   │   └── reviewer.py
│       │   │
│       │   ├── universal/
│       │   │   ├── project_analyzer.py
│       │   │   ├── architect.py
│       │   │   ├── game_designer.py
│       │   │   ├── implementer.py
│       │   │   ├── debugger.py
│       │   │   ├── code_reviewer.py
│       │   │   └── documentation.py
│       │   │
│       │   ├── game_design/
│       │   │   ├── mechanics_agent.py
│       │   │   ├── level_design_agent.py
│       │   │   ├── economy_agent.py
│       │   │   └── balancing_agent.py
│       │   │
│       │   ├── engines/
│       │   │   ├── phaser/
│       │   │   │   ├── phaser_agent.py
│       │   │   │   ├── scene_agent.py
│       │   │   │   ├── physics_agent.py
│       │   │   │   └── ui_agent.py
│       │   │   │
│       │   │   ├── unity/
│       │   │   │   ├── unity_agent.py
│       │   │   │   ├── gameplay_agent.py
│       │   │   │   ├── physics_agent.py
│       │   │   │   ├── animation_agent.py
│       │   │   │   └── editor_agent.py
│       │   │   │
│       │   │   ├── unreal/
│       │   │   │   ├── unreal_agent.py
│       │   │   │   ├── cpp_agent.py
│       │   │   │   ├── blueprint_agent.py
│       │   │   │   ├── material_agent.py
│       │   │   │   └── level_agent.py
│       │   │   │
│       │   │   ├── web/
│       │   │   │   ├── html_agent.py
│       │   │   │   ├── threejs_agent.py
│       │   │   │   └── babylon_agent.py
│       │   │   │
│       │   │   └── godot/
│       │   │       └── godot_agent.py
│       │   │
│       │   ├── testing/
│       │   │   ├── qa_agent.py
│       │   │   ├── gameplay_test_agent.py
│       │   │   ├── performance_agent.py
│       │   │   └── regression_agent.py
│       │   │
│       │   └── asset/
│       │       ├── asset_agent.py
│       │       ├── sprite_agent.py
│       │       ├── audio_agent.py
│       │       └── animation_asset_agent.py
│       │
│       ├── engines/
│       │   ├── base/
│       │   │   ├── adapter.py
│       │   │   ├── capabilities.py
│       │   │   └── engine_manifest.py
│       │   │
│       │   ├── phaser/
│       │   │   ├── adapter.py
│       │   │   ├── detector.py
│       │   │   ├── commands.py
│       │   │   └── validator.py
│       │   │
│       │   ├── unity/
│       │   │   ├── adapter.py
│       │   │   ├── detector.py
│       │   │   ├── editor_bridge.py
│       │   │   ├── commands.py
│       │   │   └── validator.py
│       │   │
│       │   ├── unreal/
│       │   │   ├── adapter.py
│       │   │   ├── detector.py
│       │   │   ├── editor_bridge.py
│       │   │   ├── commands.py
│       │   │   └── validator.py
│       │   │
│       │   ├── web/
│       │   │   ├── adapter.py
│       │   │   └── validator.py
│       │   │
│       │   └── registry.py
│       │
│       ├── tools/
│       │   ├── filesystem/
│       │   │   ├── read_file.py
│       │   │   ├── write_file.py
│       │   │   ├── edit_file.py
│       │   │   ├── search_files.py
│       │   │   └── project_tree.py
│       │   │
│       │   ├── terminal/
│       │   │   ├── execute_command.py
│       │   │   ├── run_tests.py
│       │   │   └── build_project.py
│       │   │
│       │   ├── engine/
│       │   │   ├── inspect_scene.py
│       │   │   ├── inspect_assets.py
│       │   │   ├── inspect_objects.py
│       │   │   └── editor_command.py
│       │   │
│       │   ├── browser/
│       │   │   ├── browser_tool.py
│       │   │   ├── screenshot.py
│       │   │   ├── console_logs.py
│       │   │   └── gameplay_interaction.py
│       │   │
│       │   ├── git/
│       │   │   ├── git_status.py
│       │   │   ├── git_diff.py
│       │   │   └── git_commit.py
│       │   │
│       │   └── registry.py
│       │
│       ├── skills/
│       │   ├── registry.py
│       │   ├── loader.py
│       │   └── resolver.py
│       │
│       ├── rules/
│       │   ├── global/
│       │   │   ├── coding_standards.md
│       │   │   ├── security.md
│       │   │   └── testing.md
│       │   ├── engines/
│       │   │   ├── phaser.md
│       │   │   ├── unity.md
│       │   │   ├── unreal.md
│       │   │   └── web.md
│       │   └── workflows/
│       │       ├── planning.md
│       │       ├── implementation.md
│       │       └── debugging.md
│       │
│       ├── workflows/
│       │   ├── feature_development/
│       │   │   ├── graph.py
│       │   │   ├── nodes.py
│       │   │   └── routing.py
│       │   ├── bug_fix/
│       │   ├── game_prototype/
│       │   ├── code_refactoring/
│       │   ├── performance_optimization/
│       │   └── build_release/
│       │
│       ├── knowledge/
│       │   ├── documentation/
│       │   ├── engine_apis/
│       │   ├── examples/
│       │   └── retrieval/
│       │
│       ├── validation/
│       │   ├── code_quality.py
│       │   ├── build_validation.py
│       │   ├── test_validation.py
│       │   └── result_validation.py
│       │
│       ├── security/
│       │   ├── permissions.py
│       │   ├── path_guard.py
│       │   ├── command_guard.py
│       │   └── sandbox.py
│       │
│       ├── observability/
│       │   ├── tracing.py
│       │   ├── metrics.py
│       │   ├── execution_logs.py
│       │   └── cost_tracking.py
│       │
│       ├── storage/
│       │   ├── checkpoints.py
│       │   ├── database.py
│       │   └── repositories/
│       │
│       └── interfaces/
│           ├── cli/
│           ├── api/
│           └── dashboard/
│
├── prompts/
│   ├── system/
│   ├── agents/
│   └── workflows/
│
├── skills/
│   ├── common/
│   ├── game-design/
│   ├── phaser/
│   ├── unity/
│   ├── unreal/
│   ├── web-3d/
│   └── testing/
│
├── project_templates/
│   ├── phaser-typescript/
│   ├── unity-2d/
│   ├── unity-3d/
│   ├── unreal-cpp/
│   └── threejs/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── agents/
│   ├── tools/
│   ├── engines/
│   └── workflows/
│
├── scripts/
│   ├── setup.py
│   ├── index_docs.py
│   └── inspect_project.py
│
└── data/
    ├── vector_store/
    ├── memory/
    └── execution_logs/
