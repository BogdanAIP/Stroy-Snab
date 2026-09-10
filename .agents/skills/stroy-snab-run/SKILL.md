---
name: stroy-snab-run
description: Continue governed Stroy-Snab development from live repository state. Use when the user asks to run, continue, develop or inspect Stroy-Snab without specifying a narrower skill.
metadata:
  version: "1.0"
  project: "Stroy-Snab"
---

# Stroy-Snab Run

This is a navigation/continuation skill, not independent acceptance authority.

1. Resolve live GitHub state first: main, open PRs, current heads, CI/reviews.
2. Follow `AGENTS.md` bootstrap from the exact current ref.
3. Read `docs/CURRENT_STATE.md` and identify the next canonical action.
4. If an existing active PR owns that action, continue it rather than opening overlapping work.
5. If a new stage/major component decision begins, invoke `stage-research` before production implementation.
6. Prefer experiments and existing components over new framework code.
7. Keep raw private procurement documents outside public GitHub.
8. Update canonical state/evidence documents only when their truth changes.
9. Never treat this skill as a substitute for the fresh `code-review` required for terminal acceptance.

When no implementation is yet authorized, perform the next research/evaluation action instead of inventing production code.
