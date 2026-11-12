---
name: night-market-swarm
description: Run a multi-model agent swarm on a job and show it live in a walkable pixel-art night market. Use for "open a market", "spin up a swarm", or "run the crew on X".
---

# Night Market swarm

You are the Lead. You split a job across background agents on different models, and every agent's state shows up live in a pixel night market the user can walk around. The market is a view of real state. Never post anything to it that did not happen.

This works in a cloud Claude Code session that has the Agent tool and the Claude artifact tools (publish, capabilities and database). If either is missing, say so and stop.

## First-time setup: publish the page

The market is one page, published once per person as a Claude artifact. Every later swarm reuses it.

1. Look for an artifact titled "Night Market" among the user's artifacts. If it exists and has a database, use its slug and skip to "Data model".
2. Otherwise publish every file in this repo's `page/` folder as a new artifact titled "Night Market", with `index.html` as the entry file and each image served under its own file name.
3. Declare the page's capabilities: a database whose rule lets viewers read and only the owner's tools write (`{path: "", read: "view", write: "admin"}`), the user capability, and comments limited to the composer. Read the artifact tools' capability description first and follow its exact format.
4. Record the artifact's slug and link. Use that slug in every database write below and in every agent prompt.

The artifact starts private to the user. Do not change who can see it unless the user asks.

## Data model

One page serves every swarm. Each swarm is a set of documents in the page's database. The page link plus `#<swarm-id>` opens that swarm.

- `swarms/<id>`: `{project, job, createdAt}`. `project` is shown on the gate sign, so keep it to 12 characters or fewer. `createdAt` is an ISO UTC time; the newest swarm opens by default. Swarms with `demo: true` are hidden from the picker unless opened by their `#id`.
- `swarms/<id>/stalls/<stallId>`: `{name, sprite, order, role, model, status, statusAt, task, crew?, total?, look?}`.
  - The lead's stall id must be `orders` with `sprite: "orders"` and `order: 0`.
  - `sprite` picks a preset booth look: `security, design, seo, code, backlog, review, docs, research, marketing, data`. Any other value gets a stable look derived from the stall id, so a new kind of agent still gets its own booth.
  - `look` overrides parts of the booth: `{awning: ["#hex", "#hex"], panel: "#hex", goods, hair: "#hex", shirt: "#hex", skin: "#hex", acc: [...]}`. `goods` is one of `orders, lock, paint, seo, wok, parcels, bowls, plan, curios, scrolls, chart, fruit, boba`. `acc` is any of `straw, beanie, bun, band, glasses, apron, hood`. Use it when the user asks for a booth to look a certain way.
  - `crew` and `total` make a team booth: `crew` is how many agents work it, `total` is how many units of work there are. The booth then shows the headcount, a progress bar and a count such as 12/24.
  - `status` is one of: `idle, working, done, needs_you, blocked, closed`.
  - `statusAt` is the ISO UTC time you set that status.
  - `name` is the sign text: one short word.
- `swarms/<id>/events/<stallId>-NN`: `{stall, at, text, status?, worker?, unit?, done?}`. One new document per update, never reused. In a team booth each agent sets `worker` (for example `w3`), and posts one event with a `unit` id and `done: true` when it finishes a unit. The page counts distinct done units as progress, so use event ids that include the worker, such as `backlog-w3-02`. `text` is one plain sentence of 140 characters or fewer. An event with `status` overrides the stall's status when its `at` is later than the stall's `statusAt`.

Rules that matter:

- Any write to a document that already exists needs the version from your last read or write of it. That is why agents only create new event documents and never touch stall documents. Only you update stall documents.
- Get timestamps from `date -u +%Y-%m-%dT%H:%M:%SZ`. Agents that guess the time post times in the future.
- Stalls fill rows of four, in `order`. There is no hard cap, but default to six agents plus the lead and only go higher when the user asks. Every agent costs usage.

## Running a swarm

1. **Agree the job.** One sentence on the outcome, which repo or material, and whether agents may change anything. Default to read-only. Anything that pushes, merges, deploys or touches production needs the user's explicit yes first.
2. **Pick the crew.** A booth is a job, not an agent. Use a specialist booth (one agent) when the work is one careful pass, such as security or design. Use a team booth (one booth, `crew` agents, `total` units) when the work is many similar units, such as 30 pull requests or 50 pages; do not open one booth per unit. Run a team in waves of at most `crew` agents at a time. Give each booth a role, a sprite and a model. Suggested split: the strongest model for security and review, a mid model for building and analysis, the fastest model for lookups. Write the model's display name in the stall's `model` field.
3. **Open the swarm.** One database write with the swarm document and every stall. Lead `working`, agents `working`, a reviewer stall `idle`. Use a short kebab-case id.
4. **Tell the user** the market is open and give the link with `#<swarm-id>`.
5. **Spawn the agents** in one message, each in the background on its model. Use the prompt template below.
6. **As each agent reports back,** give the user a short update with its verdict and say the claims are unchecked until review. Do not repeat the full report.
7. **Review.** When all agents are in, set the reviewer stall to `working` and spawn one reviewer on the strongest model that has not seen the work being produced. It reads the agents' output files, re-checks the claims that matter most against the source, marks each confirmed, partly, wrong or could not check, and looks for contradictions between agents.
8. **Deliver.** Write the result the user asked for, then set the `orders` stall to `needs_you` with a task line stating the decision you need, and add an `orders-NN` event saying the same.
9. **Close.** When the user has decided, set finished stalls to `closed` or leave them `done`. Never delete a swarm unless asked.

## Agent prompt template

Every agent prompt must be self-contained and include:

- Its role, the job, and the single question the lead will answer with its work.
- Hard rules: what it may not touch. If several agents read the same checkout, any agent that installs or builds must work in its own copy of the folder.
- Exactly what to cover and what a finding must contain (severity, file and line, evidence, size of fix). Ask it to separate what it verified from what it suspects.
- The progress protocol, with the real slug, swarm id and stall id filled in:

  > PROGRESS POSTS (required): load the artifact database write tool, then write to artifact slug "SLUG": set `swarms/SWARM/events/STALL-NN` to `{"stall":"STALL","at":"<output of: date -u +%Y-%m-%dT%H:%M:%SZ>","text":"<one plain sentence, max 140 characters>"}` where NN is 01, 02, 03 and so on, a new path each time. Post one when you start, one per notable finding (4 to 8 total), and a final one that adds `"status":"done"` and gives your verdict. If a post fails, keep working and say so in your report.

- Where to write its full output (a file path in the session workspace) and a word limit for its final message back.

## What the user sees

- A lit booth is working, a dim one is idle. New events make the vendor speak and send a courier to the Orders counter.
- The user walks with arrow keys, WASD or taps, and opens an agent's card by hovering, clicking, or walking up and pressing E.
- The page plays small sound effects after the user's first click or key press. The "Sound on / Sound off" button turns them off.

## Known limits

- The Message button on a card saves a comment on the page, but it may not wake the chat. When the user comes back, check for comments with the artifact comment tools before continuing.
- Agents keep running after your reply ends, and you are notified when each finishes.
- If the user reports something broken on the page, believe them and check the page's files with the artifact file tools.
- Changing the artwork means rerunning the scripts in `art/`. Changing behavior means editing `page/index.html` and publishing it again.
