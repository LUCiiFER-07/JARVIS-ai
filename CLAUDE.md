# JARVIS-AI — Claude Code Development Instructions

## 1. PROJECT MISSION

JARVIS-AI is an existing modular Python project for building a powerful
JARVIS-style personal AI assistant for Windows.

This is NOT a new project.

The project already contains working functionality that must be preserved.

The long-term goal is to evolve JARVIS into a modular AI assistant supporting:

- Voice interaction
- Speech-to-text
- Text-to-speech
- Wake-word detection
- AI/LLM conversation
- Multiple AI providers
- Intent routing
- Tool execution
- Desktop automation
- Web search
- Browser automation
- Awareness/context
- Memory
- Workspaces
- Workflows
- Vision/multimodal input
- System telemetry
- Authority/permissions
- Sub-agents
- Proactive intelligence
- Long-term goals
- A futuristic JARVIS HUD
- Optional secure phone integration

Development MUST happen incrementally.

Do not attempt to build the entire final architecture at once.


# 2. CURRENT VERIFIED BASELINE

Before Claude Code integration, the repository was manually verified.

Baseline Git commit:

9be46a9

Commit message:

Checkpoint before Claude Code integration

Baseline verification:

- `python -m pytest -v`
  - 19 tests passed

- `ruff check .`
  - All checks passed

The repository was clean when the Claude integration process began.

This baseline is a rollback point.

Do not destroy or unnecessarily rewrite working functionality introduced
before this commit.


# 3. IMPORTANT: THIS IS AN EXISTING PROJECT

Always inspect the repository before proposing architectural changes.

Never assume files, classes, methods, dependencies, or APIs exist without
checking them.

Never rebuild a working module simply because another architecture appears
cleaner.

Prefer:

EXTEND → ADAPT → REFACTOR CAREFULLY

instead of:

DELETE → REWRITE EVERYTHING


# 4. CURRENT WORKING CAPABILITIES

The project already contains working implementations for several important
features.

Preserve them unless the active development phase explicitly requires a
carefully tested modification.

Existing capabilities include:

- Windows microphone discovery
- Multiple microphone support
- Saved microphone selection
- Dynamic input channel handling
- Mono/stereo microphone compatibility
- Device-specific sample-rate handling
- Audio recording
- Voice Activity Detection (VAD)
- Background-noise calibration
- Speech-start timeout
- Silence-based recording termination
- Maximum recording duration
- WAV file creation
- Audio validation
- Faster-Whisper speech recognition
- English speech transcription
- Continuous command loop
- Command model
- Deterministic command parser
- Command executor
- Greeting command
- Time command
- Exit command
- Basic calculator
- Natural-language calculation work in progress
- Central logging
- Custom exception handling
- Pytest tests
- Ruff linting


# 5. CURRENT PROJECT AREAS

Important existing project areas include:

- `main.py`
- `core/`
- `voice/`
- `speech/`
- `utils/`
- `tests/`
- `config/`
- `requirements.txt`
- `pyproject.toml`

Before modifying any of these areas:

1. Inspect the relevant files.
2. Understand their current interfaces.
3. Search for usages.
4. Check their tests.
5. Explain why a change is required.


# 6. ACTIVE DEVELOPMENT STRATEGY

JARVIS is being rebuilt according to a phased architecture roadmap.

The immediate architecture direction includes:

1. Baseline protection
2. Voice reliability
3. Deterministic command understanding
4. Runtime foundation
5. State management
6. Event system
7. Tool registry
8. Authority/permission engine
9. Text-to-speech
10. Wake-word/listening modes
11. AI brain
12. Model routing
13. AI-assisted intent routing
14. Live web search
15. Desktop tools
16. Awareness/system telemetry
17. Browser automation
18. Memory
19. Workspaces
20. Workflow engine
21. Vision/multimodal input
22. JARVIS HUD
23. Scheduler/proactive intelligence/goals
24. Sub-agents
25. Secure phone integration

Do not skip ahead to a later architectural capability unless explicitly
requested.


# 7. CURRENT ACTIVE PHASE

Current phase:

PHASE 1 — VOICE RELIABILITY HARDENING

Phase 0 — BASELINE FREEZE AND ARCHITECTURE CONTRACT: COMPLETE
Phase 0 completion commit: bd53cbe

The purpose of Phase 1 is to harden the EXISTING working voice pipeline.

Existing working functionality that must be preserved:
- Windows WASAPI microphone discovery
- Multiple microphone support
- Saved microphone selection
- Device-specific sample rates
- Dynamic channel handling
- Mono/stereo compatibility
- VAD
- Background calibration
- Pre-roll
- speech-start timeout
- silence-based termination
- maximum recording duration
- WAV recording
- AudioValidator
- Faster-Whisper
- continuous listening

VERIFIED PHASE 1 ISSUES:
1. VAD/background calibration currently executes on every recording.
2. The calibration threshold can vary significantly between commands.
3. Calibration currently consumes part of speech_start_timeout because the timeout clock starts before calibration completes.
4. Whisper can successfully return empty/whitespace transcription text, which is currently routed as an UNKNOWN command.

PHASE 1 SUB-PHASES:
- Phase 1A — Diagnosis and implementation planning: COMPLETE
- Phase 1B — VAD calibration persistence and speech-start timeout correction: NEXT
- Phase 1C — Empty transcription handling
- Phase 1D — Full regression and three-microphone manual acceptance

During Phase 1 DO NOT implement:
- TTS
- wake word
- AI/LLM integration
- JARVIS Runtime
- State Manager
- Event Bus
- Tool Registry
- Authority Engine
- Desktop automation
- Browser automation
- Memory
- Workspaces
- Workflows
- Agents
- Vision
- HUD/UI
- Phone integration

Do not replace Faster-Whisper.
Do not replace the existing RMS-based VAD.
Do not introduce WebRTC VAD or another VAD dependency during this phase unless later explicitly approved because the existing implementation has been proven inadequate.
Do not reorganize the repository.


# 8. CLAUDE CODE WORKFLOW

Whenever Claude receives a development task, follow this order.

## Before editing

1. Read this `CLAUDE.md`.
2. Inspect the repository.
3. Check `git status`.
4. Read the files related to the requested task.
5. Search for usages of anything being modified.
6. Read relevant tests.
7. Run the existing tests when appropriate.
8. Run Ruff when appropriate.
9. Understand the current behavior.
10. Explain the intended change before making major architectural edits.

Do not begin with a large rewrite.


## During implementation

Modify only what is required for the currently approved task.

Prefer small, reviewable changes.

Do not silently expand the scope.

If the task requires an architectural decision with significant trade-offs,
explain the options before performing the major change.


## After implementation

Run:

```powershell
ruff check .