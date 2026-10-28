# Subagent Delegation & Role Rules

When handling complex tasks, delegate to specialized subagents to isolate context and optimize reasoning tiers:

1. **`explore`** (`.agents/agents/explore.md`) — **Flash · Low Thinking**
   - **When to use:** Rapid file searches, symbol tracking, directory scans, and architectural navigation.
   - **Role:** Pure read-only scouting that summarizes file paths and snippets without polluting the main context.

2. **`plan`** (`.agents/agents/plan.md`) — **Flash · High Thinking**
   - **When to use:** Designing implementation roadmaps, multi-step refactoring plans, or analyzing edge cases.
   - **Role:** Deep deliberation against project constraints (`AGENTS.md`, 2048-byte sector alignments, binary structures) before code is touched.

3. **`debugger`** (`.agents/agents/debugger.md`) — **Flash · High Thinking**
   - **When to use:** Game engine crashes, crash offsets (RIP), stack traces, access violations (`0xC0000005`), or softlocks.
   - **Role:** Systematic register delta analysis (%r10, %rdx, %rcx), SLLZ stream underflows, and disassembling faulting instructions without guesswork.

4. **`code-reviewer`** (`.agents/agents/code-reviewer.md`) — **Flash · Medium Thinking**
   - **When to use:** Pre-commit audits and code review before release packaging.
   - **Role:** Audits diffs strictly against the 10 Golden Rules of `AGENTS.md` (no `copy /y`, 2048-byte sector alignment, 58-char phone booth strings, no truncated tables).

5. **`scout`** (`.agents/agents/scout.md`) — **Flash · Medium Thinking**
   - **When to use:** Searching external documentation, API references, library source, or reverse-engineering articles.
   - **Role:** Balanced reasoning to filter relevant Sega RGG engine specs without getting bogged down in slow inference.

6. **`verifier`** (`.agents/agents/verifier.md`) — **Flash · Low Thinking**
   - **When to use:** Quality assurance, regression testing, and post-build verification.
   - **Role:** Executes `verify_patch.py` (131/131 OK), phone booth 58-character ASCII checks, and Bob Utsunomiya size assertions.
