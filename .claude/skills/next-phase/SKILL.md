---
name: next-phase
description: Orchestrator step. Review the last tutor handoff, update state and docs, then prepare the next phase brief and its code blanks.
---

# Next phase (orchestrator)

Keep this session small. Read only what is listed here, plus the files a
brief or handoff names.

## 1. Load context

- `.handoff/STATE.md`: current phase, private facts, open follow-ups.
- `docs/phases/README.md`: the phase list.
- The newest `.handoff/NN-*.md` that STATE.md hasn't recorded as reviewed.
- Don't read `docs/PLAN.md` unless the phase needs its detail, and then
  only the relevant section.

## 2. Review the handoff (skip if none)

- Read the files the user changed and run the brief's check command.
- Give feedback in a few lines: what's right, one thing to improve.
  Don't rewrite their code.
- Answer the "For the orchestrator" items, or ask the user if one is
  genuinely their decision.
- Update `.handoff/STATE.md`: mark the phase reviewed, add new facts and
  decisions, drop follow-ups that are done. Keep it under ~80 lines.
- Move finished items in `LEARNING.md` to Done.
- Add a short entry in the private journal (path in STATE.md): what was
  done, what was hard, a blog angle if there is one.

## 3. Prepare the next phase

- Take the next row in `docs/phases/README.md`. If it needs the server
  and STATE.md says there's no access, take the next row that doesn't.
- Write the boilerplate and the `...` blanks. Each blank is one
  expression or line, with the API explained in a comment above it, and
  must fail until filled. `TODO(you) [TAG]` on every blank.
- Write `docs/phases/NN-name.md` with sections: header (plan phase,
  tags), Goal, Context (facts from STATE.md the tutor needs, no private
  values), Files, Concepts, Check, Done when. For ops phases, add a
  Runbook section with exact commands and the data safety rules from
  PLAN.md that apply.
- Run pre-commit on the new files.
- Tell the user, in two lines, which tutor model to start, and stop.
