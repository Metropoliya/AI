---
name: council
description: Run a question, decision, or idea through an agentic 5-advisor council. Five advisor subagents argue from independent, locked perspectives in parallel — each in its own isolated context — optionally over multiple debate rounds, then a Chairman subagent renders a verdict. Use this skill ONLY when the user explicitly invokes it by name — phrases like "run this through the council", "council this", "convene the council", "use the council skill", "give this to the council", "pressure-test this with the council", or similar explicit invocations. It is heavy by design (six or more subagents per session) and should not fire on ordinary decision-shaped questions.
---

# Council

An agentic pressure-test for questions, decisions, and ideas.

Five advisors with locked thinking styles run as **parallel subagents** — each in
its own isolated context, so none of them sees the others while it writes. They
optionally argue across 1–3 debate rounds, then a **Chairman** subagent (a pure
judge, no new arguments) renders the verdict.

## Why subagents

If one model writes all five voices in a single context, it knows what the other
voices will say while writing each one, so the "disagreement" comes out
cosmetic — five lanes that quietly complement each other. Running each advisor as
a **separate subagent with no shared context** is what lets them contradict each
other, argue from incompatible premises, and refuse to converge. That independence
is the whole point; protect it.

## When to invoke

Trigger ONLY on explicit invocation ("council", "run this through the council",
"pressure-test this with the council", or similar). If the user asks a
decision-shaped question without invoking the skill, answer normally — convening
the council means spawning six-plus subagents, which is slow and expensive, and is
only justified when asked for.

If the input is ambiguous about *what* should be pressure-tested (e.g. just
"council this please"), ask exactly **one** clarifying question, then proceed. Do
not interview them.

## The advisors

Each persona lives in `prompts/<key>.md` and is fed verbatim to its subagent.

| Key | Advisor | Angle |
|---|---|---|
| `contrarian` | The Contrarian | Finds the fatal flaw |
| `first_principles` | The First Principles Thinker | Asks if you're solving the right problem |
| `expansionist` | The Expansionist | Finds the upside everyone missed |
| `outsider` | The Outsider | Catches the curse of knowledge |
| `executor` | The Executor | Cares only what you do Monday morning |

The **Chairman** persona is `prompts/chairman.md`. The Chairman runs last, reads
the full transcript, weighs it, and must pick a single most-right advisor and
commit to a recommendation.

## Workflow

Set up a working directory for the session first — e.g. `council-<short-slug>/`
in the current directory. The subagents hand off through files in it, which keeps
each advisor's text out of your context until assembly (preserving independence
and keeping things lean). The layout you build up:

```
council-<slug>/
    framed.txt              # the neutral framed question (you write this)
    round-1/                # one file per advisor, written by the advisor subagents
        contrarian.md  first_principles.md  expansionist.md  outsider.md  executor.md
    round-2/                # only if running debate rounds
    verdict.md              # written by the Chairman subagent
    session.md              # final artifact (you assemble this — step 5)
```

### 1. Confirm and frame

Repeat the question back in one sentence so the user can correct you. Then write a
**neutral framing** of it to `framed.txt`: the core decision in one sentence, the
key context and constraints the user gave (preserve specifics), and what's at
stake. Do not editorialize, signal a lean, or add your own opinion — this single
text is what all five advisors receive, so any bias here contaminates all of them.
You can write the framing yourself; it isn't an advisor role.

### 2. Dispatch the five advisors in parallel

In a **single turn**, spawn all five advisor subagents at once so they run
concurrently and independently. Give each subagent a prompt that:

- tells it to read its persona from `prompts/<key>.md` and the framed question from
  `framed.txt`;
- tells it to **respond only to the persona and the framed question, ignoring any
  repository files, CLAUDE.md, available skills, or project context** — those are
  irrelevant to the advisory task and must not leak into the response;
- tells it to write **only its response text** (no preamble, no commentary, no
  headings) to `round-1/<key>.md`, and not to read any other advisor's file.

Keeping the advisor text in files (not in your reply) is what preserves the
isolation — don't have them report their answers back to you inline.

### 3. (Optional) debate rounds

For round 2+, each advisor responds again after seeing the others — but **anonymized,
so they engage with arguments, not authors**. Anonymization is what keeps the debate
honest; get it exactly right.

For each advisor, build its peer block from the *previous* round's files:

- take the other four advisors' responses — **omit this advisor's own**;
- drop any that are empty/errored;
- put them in a shuffled order (don't preserve the canonical advisor order — that
  would leak identity), and label them `--- Response A ---`, `--- Response B ---`,
  etc.;
- never name the authors or hint at which angle wrote which.

Spawn the five advisor subagents again — same persona and framed question, plus
their own peer block — and have each write to `round-2/<key>.md`, sharpening,
attacking, or doubling down while staying in its angle. Double-check before
dispatching that no advisor's peer block contains its own previous response.

See "Choosing the round count" for when this is worth it.

### 4. Chairman

Spawn one Chairman subagent. Tell it to read `prompts/chairman.md`, `framed.txt`,
and every advisor file across all rounds, then write the verdict (following the
exact structure in its persona) to `verdict.md`.

### 5. Assemble and report

Stitch the session into `council-<slug>/session.md` in this order, preserving the
advisor text verbatim (copy the files; don't rewrite them):

```
# Council session

## The question
<contents of framed.txt>

## The advisors            (use "## The advisors — round N" if multi-round)
### The Contrarian
<contents of round-1/contrarian.md>
### The First Principles Thinker
...continue in this fixed advisor order: Contrarian, First Principles,
   Expansionist, Outsider, Executor...

<contents of verdict.md>
```

Keep the advisors in that fixed order regardless of which subagent finished first.
If an advisor file is missing or empty, note the slot as `_[advisor did not
respond]_` rather than dropping the heading — the Chairman still ruled on the rest.

Then **briefly summarize the verdict** in your reply — 2–3 sentences pointing at
the Chairman's recommendation — and link the file. Do NOT paraphrase or rewrite the
advisor responses; they are the artifact, and the user wants to read them as-is.

## Choosing the round count

Choose based on the stakes of the question, not the user's enthusiasm:

- **1 round** (default): most questions. One sweep of advisors, then verdict. Fast
  and cheap. A single round rarely produces sharp inter-advisor conflict — the
  voices cover different ground but don't yet clash — so it's right when you want
  five angles, not a fight.
- **2 rounds**: substantial decisions where the advisors are likely to disagree in
  interesting ways (career, strategy, product direction). The cross-feed in round 2
  is where genuine disagreement actually surfaces, because each advisor reacts to
  positions it didn't write.
- **3 rounds**: only for genuinely high-stakes or deeply contested questions, where
  you want to see whether positions converge or harden across exchanges.

If the user doesn't specify, default to 1 and offer to escalate after they read it.

## Output structure

`session.md` contains:

- `## The question` — the neutral framing
- `## The advisors` (or `## The advisors — round N` if multi-round) — five responses
  per round
- `## Verdict` — the Chairman's ruling: What survived / What didn't / Most right /
  Recommendation / A note on this council

## Cost

The user is spending real model calls. A 1-round session is six subagents (five
advisors + Chairman); each added round is five more. Subagents are lighter than
they look — each carries only the small persona and the framed question — but six-
plus of them per session is still real spend. Mention the round-count cost when the
user escalates or runs several sessions back to back.

## Failure modes

- **An advisor subagent fails or writes nothing.** `assemble` notes the empty slot
  as a dropped voice and the Chairman still rules on the rest. Mention it to the
  user if it happens; offer to re-run that one advisor.
- **An advisor's response leaks meta-commentary** (about skills, the repo, or these
  instructions). That means the clean-context instruction in step 2 didn't take —
  re-run that advisor, reinforcing "respond only to the persona and the framed
  question." Don't ship a contaminated response.
- **The user invoked the skill but the question is trivial.** Push back gently:
  "This doesn't really need the council — happy to just answer directly. Want me to
  run it anyway?"

## Anti-patterns

- **Don't collapse the council into one context.** Spawning the advisors as
  subagents is the entire value. Never role-play all five yourself in one pass to
  "save time" — that produces exactly the cosmetic agreement the council exists to
  avoid.
- **Don't paraphrase the advisors.** Their outputs are the value. Quote a heading
  and point at `session.md`.
- **Don't second-guess the Chairman in your reply.** You may note if you think the
  verdict is wrong, but the user convened a separate judge on purpose — don't dilute
  it.
- **Don't run the council on every decision-shaped question.** It's heavy by design.
- **Don't promise rounds you didn't run.** If the user asked for 2 rounds and you
  ran 1, fix it — don't describe what round 2 would have said.

## Files in this skill

- `SKILL.md` — this file
- `prompts/contrarian.md`, `first_principles.md`, `expansionist.md`, `outsider.md`,
  `executor.md` — the five advisor personas
- `prompts/chairman.md` — the Chairman persona

That's the whole skill: instructions plus six personas. The orchestration is the
subagent dispatch described above — no scripts to install or run.
