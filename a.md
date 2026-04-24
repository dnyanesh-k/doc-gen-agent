# ARIA — Engineer learning path (start → productive)

**Purpose:** A **sequenced** way to learn `arcadia-aria` without reading folders at random. This is a **roadmap of what to read and in what order**, with pointers into code and the architecture doc.

**Pair with:** [`ARIA-TECHNICAL-SYSTEM-DESIGN.md`](./ARIA-TECHNICAL-SYSTEM-DESIGN.md) (system design, diagrams, component map) — use it as a **companion** while you go through the phases below.

**Assumption:** You will clone the repo and use the top-level `README.md` for install prerequisites (Python 3.12+, Node 20+, git) and any org-specific access (SSO, VPN for LiteLLM) when you actually run the launcher.

---

## How to use this document

- Follow **phases in order** the first time; skimming later is fine.
- **Hands-on** steps are short — they make abstract paths concrete (`search_kb`, hooks, `brain/` reads).
- If you only care about one area (e.g. MCP routing, or WFA XML), jump to **§6 Deep-dive tracks** after Phase 1–2.

---

## Phase 0 — One-time environment (before “understanding” the code)

1. Open **`README.md`** (root) and complete **Installation** and whatever **AWS / auth** sections your role needs so `aria` can start.
2. Note **repo layout** in README’s `Repo Layout` — it is the same mental model the rest of the learning path uses.

*Checkpoint:* `aria` launches Claude Code in a project directory, or you know which README section blocks you (e.g. SSO) and you can still read the repo offline.

---

## Phase 1 — The smallest end-to-end picture (30–60 min)

**Goal:** Know what runs, where the “brain” lives, and that retrieval is explicit.

| Step | What to do | Why it matters |
|------|------------|----------------|
| 1.1 | Read **`docs/ARIA-TECHNICAL-SYSTEM-DESIGN.md` §1–3** (Purpose, Repository map, High-level architecture) + skim the mermaid diagrams | You get a single **system picture** before diving into files. |
| 1.2 | Open **`system-prompt.md`** (header + “Search KB Before Everything” + “Core Rules” table) | This is the **model contract**; every other piece exists to support or enforce it. |
| 1.3 | Open **`brain/routing.md`**, read **intro + one full subsection** (e.g. a workflow you recognize) | You see how **triggers** become `brain/...` paths—input to `search_kb`. |
| 1.4 | Skim **`.claude/mcp.json`** and **`brain/mcp/mcp_server.py`** (`search_kb` function only) | Connects “routing” to **MCP** and the **list of query phrases** API. |

*Checkpoint:* You can explain: “The model is told to call `search_kb` first; that uses embeddings over `routing.md` to point at markdown under `brain/`.”

---

## Phase 2 — Launcher and configuration (45–60 min)

**Goal:** Know how the host wires Claude Code to this repo.

| Step | What to read | Why |
|------|----------------|-----|
| 2.1 | **`aria`** (start: `ARIA_ROOT` resolution, then search for `claude` / `--append-system-prompt` / `--settings`) | See how **`ARIA_ROOT`**, system prompt, and settings enter the process. |
| 2.2 | **`.claude/settings.json`**: `permissions` + `hooks` + `mcp` allow entry | **Static** deny list and hook wiring. |
| 2.3 | **`.claude/mcp.json`** (full) | Confirms stdio MCP server path and command. |

*Optional hands-on:* Run **`python brain/mcp/mcp_server.py`** only if you are debugging MCP (it expects stdio from a client; otherwise just read the code). Prefer reading **`routing_core.py`** and **`build_routing_index.py`** names/exports.

*Checkpoint:* You can name the two config files the launcher relies on (`settings` + mcp) and what hooks fire on session start and before tools.

---

## Phase 3 — Safety and identity (60–90 min, high leverage)

**Goal:** Separate “denylist in JSON” from “persona in session file.”

| Step | What to read | Why |
|------|----------------|-----|
| 3.1 | **`.claude/hooks/pre_tool_use.py`** (file header + `main` through first `authorize`) | **Dynamic** gate; see why `session_id` and **session file** matter. |
| 3.2 | **`.claude/hooks/session_start.py`** (identity resolution order in docstring + `main` flow) | How **`ARIA_PERSONA`** gets set without trusting env in `pre_tool_use`. |
| 3.3 | Skim **`personas/persona-registry.yaml`** + read **one** profile, e.g. **`personas/profiles/engineer.yaml`** | See YAML shape: bash patterns, capabilities, environments. |
| 3.4 | **`.claude/hooks/_persona_lib.py`** — read **module docstring** + jump to `load_profile` / `authorize` (names only, not every line) | This file is large; know **what** it does, not every branch on day one. |

*Checkpoint:* You can explain: static denies in `settings.json` + per-persona **authorize** in hooks using **session state**, not `ARIA_PERSONA` from the shell.

---

## Phase 4 — Brain content: modules vs knowledge vs skills (45 min)

**Goal:** Know where procedures vs facts vs packaged workflows live.

| Step | What to do | Why |
|------|------------|-----|
| 4.1 | Read one **`brain/modules/*.md`** file end-to-end (e.g. `jira.md` or `sdd-workflow.md`) | Modules are **procedure shells** and pointers to cards. |
| 4.2 | Open **2–3 files** in **`brain/knowledge/<any-domain>/`** that match your work | Cards are **atomic** domain facts and commands. |
| 4.3 | Read **`docs/SKILL-DAG-BOUNDARY-SPEC.md`** §Purpose + §Split (SKILL vs DAG) | Unlocks how **`.claude/skills/*`** relate to tested Python and to automation. |
| 4.4 | Open **one** `.claude/skills/<name>/SKILL.md` (e.g. a smaller one) | Skills are **opinionated** workflow packages, not the same as a single card. |

*Checkpoint:* You can place a random task: “Is this a card update, a routing row, a new module section, or a new skill package?”

---

## Phase 5 — Tests and change safety (30–60 min)

**Goal:** See how behavior is locked in for automation-heavy areas.

1. List **`tests/`** — file names map to subsystems (`test_wfa_*.py`, `test_persona_lib.py`, `test_build_routing_index.py`, …).
2. Read **`pyproject.toml`** (pytest + ruff only) to see **how** tests are run.
3. Run **`pytest -q tests/test_build_routing_index.py`** (or one small file) in the repo venv if available — confirms your checkout.

*Checkpoint:* You know where to add a test when you change routing, persona auth, or WFA builders.

---

## Phase 6 — Deep-dive tracks (pick 1+)

| Track | Start here | Then |
|-------|------------|------|
| **Semantic routing** | `brain/mcp/routing_core.py` (`parse_routing_md`, `search`, `multi_search`) | `tests/test_build_routing_index.py`, tweak `brain/routing.md` locally and rebuild index |
| **MCP / embeddings** | `mcp_server.py` + `ARIA_INDEX_REBUILD` in docstring | `build_routing_index.py`, `~/.aria/.cache/routing-index.json` role |
| **WFA / connector XML** | `tests/test_wfa_xml_builder.py` (one test class) | `.claude/skills/cm-wfa-resolution/`, `brain/scripts` (as referenced in tests) |
| **Jira / sibling automation** | `brain/scripts/sibling_finder.py` (entrypoints) | `config/mirror_constants.yaml`, `tests/test_sibling_finder.py`, `validate_mirror_constants.py` |
| **LiteLLM / token** | `scripts/fetch-litellm-token.py` | `tests/test_fetch_litellm_token.py` |

---

## Suggested “day 1 / day 2 / day 3” split

| Day | Focus |
|-----|--------|
| **1** | Phases 0–1 + skim **ARIA-TECHNICAL-SYSTEM-DESIGN** in full (30 min) |
| **2** | Phases 2–3 |
| **3** | Phases 4–5 + one **track** in Phase 6 relevant to your work |

---

## When you are “done” with first-pass onboarding

You can work effectively when you can:

- Trace a user question: **`routing.md` → `search_kb` → `Read` on a card** (per `system-prompt.md`).
- Find **static** vs **dynamic** guardrails and the **session file** in **hooks**.
- Decide whether a change belongs in **knowledge**, **routing**, a **module**, a **skill**, or **Python tests**.

For anything else, use **§11 Key files** in **ARIA-TECHNICAL-SYSTEM-DESIGN.md** as a debug index.
