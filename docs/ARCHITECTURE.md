# JARVIS-AI Architecture Contract

## 1. Project Purpose
JARVIS-AI is a modular personal AI assistant for Windows, built incrementally to evolve into a fully capable assistant with voice interaction, desktop automation, web search, and AI-driven intelligence, while maintaining a futuristic, modular design.

## 2. Current Verified Baseline
- **Working-code baseline**: 9be46a9 — "Checkpoint before Claude Code integration" (the verified, passing system).
- **Development-rules checkpoint**: 3023a9b — "Add Claude Code development instructions" (adds the repository development contract, CLAUDE.md).
System is verified with `pytest` (19 passing) and `ruff` (no issues) at the 9be46a9 baseline.

## 3. Current Repository Architecture
The project follows a modular layered architecture:
- `main.py`: Primary orchestrator.
- `core/`: Command handling, parsing, and execution.
- `voice/`: Audio recording, VAD, device management.
- `speech/`: Speech transcription, model management, validation.
- `utils/`: Centralized logging.
- `tests/`: Unit tests for core modules.

## 4. Current Runtime Flow
Microphone
→ Device Discovery / Selection
→ VoiceRecorder
→ VAD
→ WAV
→ AudioValidator
→ Faster-Whisper
→ SpeechResult
→ CommandParser
→ CommandExecutor
→ Response
→ Continuous Loop

## 5. Current Module Responsibilities
- `main.py`: Orchestrates services and runs the listening loop.
- `core/`: Deterministic command parsing and execution.
- `voice/`: Manages microphone input, VAD-based recording, and settings.
- `speech/`: Transcribes audio via Faster-Whisper, validates recordings.
- `utils/`: Centralized logging.
- `tests/`: Unit validation of core logic.

## 6. Current Architectural Invariants
- Multiple microphones must continue working.
- Microphone index must never be hard-coded.
- Different sample rates must remain supported.
- Mono/stereo microphones must remain supported.
- Faster-Whisper pipeline must remain functional.
- Deterministic commands should remain deterministic where practical.
- Existing tests must not regress.
- Existing centralized logging should be preserved.

## 7. Known Current Limitations
- Natural-language calculation incomplete.
- VAD/background calibration currently occurs for every recording, adding latency and potentially producing varying thresholds between commands.
- `main.py` owns orchestration (requires runtime abstraction).
- Blocking/synchronous command loop.
- No centralized runtime, state manager, event bus, or tool registry.
- No authority engine.
- No TTS, wake word, or AI brain.

## 8. Target Architecture (Planned/Future Components)
The components below represent the target architecture. Some already have partial foundations in the current project and will be extended incrementally; others do not yet exist. Existing working implementations must be preserved.

- JARVIS Runtime
- State Manager
- Event Bus
- Voice Engine — existing foundation: current `voice/` and `speech/` systems
- AI Brain
- Model Router
- Intent Router
- Planner
- Tool Registry
- Authority Engine
- Web Search
- Desktop Tools
- Browser Agent
- Awareness Engine
- Memory Engine
- Workspace Manager
- Workflow Engine
- Vision Engine
- Scheduler
- Sub-Agent Manager
- Goal Manager
- Notifications
- Telemetry
- Configuration System — partial foundation: existing configuration dataclasses and persisted voice settings
- Security Layer
- Logging / Observability — logging foundation already exists in `utils/logger.py`; broader observability is future work
- JARVIS HUD

## 9. Dependency Direction
*Target conceptual architecture (responsibility and control/data flow — not yet a Python import graph):*

                    JARVIS Runtime
                          │
             ┌────────────┼────────────┐
             │            │            │
          State        Event Bus     Services
             │            │            │
             └──────┬─────┘            │
                    │                  │
                 JARVIS HUD            │
              (observer/client)        │
                                       ▼
                                Brain / Intent
                                       │
                                  Tool Registry
                                       │
                                Authority Engine
                                       │
                                     Tools

*Principles:*
- The JARVIS Runtime must be able to operate without the HUD.
- The HUD consumes state/events and sends user requests; it does not own application lifecycle or business logic.
- The LLM must not directly control the operating system.
- Tool execution must eventually pass through the Authority Engine.
- Web Search and Browser Automation remain separate capabilities.

## 10. Runtime Lifecycle Contract (Planned/Future)
*Planned lifecycle concepts:*
start, pause, resume, disable listening, cancel task, shutdown, health check.

## 11. State Machine Contract (Planned/Future)
*Planned states:*
OFFLINE, INITIALIZING, IDLE, LISTENING, TRANSCRIBING, THINKING, SEARCHING, USING_TOOL, EXECUTING, WAITING_FOR_PERMISSION, SPEAKING, PAUSED, ERROR.

## 12. Tool Contract (Planned/Future)
*Planned tool fields:*
name, description, input schema, permission/risk level, timeout, handler, result, error handling.

## 13. Authority Contract (Planned/Future)
*Planned permission model:*
L0 READ, L1 SAFE ACTION, L2 CONFIRMATION REQUIRED, L3 RESTRICTED.
Significant actions must eventually be mediated by the Authority Engine.

## 14. AI Brain Contract (Planned/Future)
- Must support provider abstraction.
- Must avoid coupling JARVIS permanently to one model/provider.
- Must preserve deterministic handling for simple commands.
- Must route complex requests to AI only when needed.

## 15. Hardware Constraints
- The system runs on consumer Windows hardware.
- Must avoid: huge always-loaded models, excessive concurrent agents, unnecessary constant inference, excessive background processes.

## 16. Development Rules
BUILD → RUN → TEST → MANUALLY VERIFY → FIX → REGRESSION TEST → CHECKPOINT → COMPLETE.

## 17. Phase Boundaries
PHASE 0: Baseline + architecture documentation only.
PHASE 1: Voice reliability hardening.
PHASE 2: Deterministic intent/command core.
PHASE 3: Runtime foundation.
PHASE 4: Central state manager.
PHASE 5: Event bus.
PHASE 6: Tool contract and registry.
PHASE 7: Authority/permission engine.
*Later phases must not be implemented early.*