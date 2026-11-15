# SentiTriage-ES design system

The interface has one job: show what the agent decided and why, so a person can trust it or
take over. Its identity comes from the product's core idea: **the agent knows when not to
decide**. The threshold τ is the signature element and owns the only accent color.

## Principles

1. **Decision first.** The verdict (action + plain-language title + reason) is the largest
   element on screen. Probabilities and confidence support it; they never compete with it.
2. **Decisions and sentiment never share a visual language.** Actions (PASS, QUEUE,
   ABSTAIN) use color *and* shape. Sentiment classes (negative, neutral, positive) are what
   the model believes, so they are drawn in ink: the best guess dark, the rest grey.
3. **One accent.** Marigold marks the threshold τ and the abstention zone, and nothing else.
4. **Real data only.** Every number on screen comes from the API (`/classify`,
   `/classify/batch`, `/model`). The sample texts are real comments (Correa, 2019, CC BY 4.0).
5. **Group by space, not by boxes.** Sheets hold inputs and tables; the decision sits on the
   page background and is structured by type size and rules.

## Tokens

| Token | Value | Use |
|---|---|---|
| `--ink` | `#13213A` | Text, app bar, primary button, best-guess bar |
| `--bg` | `#EEF1F0` | Page background (cool mist) |
| `--surface` | `#FFFFFF` | Sheets, lanes, dialog |
| `--accent` | `#E9A21B` | Threshold τ, abstention zone, ABSTAIN mark |
| `--abstain` | `#8A5300` | ABSTAIN text (meets 4.5:1 on white) |
| `--queue` | `#B2302A` | QUEUE mark and text |
| `--pass` | `#1D6B52` | PASS mark and text |
| `--sent-other` | `#A3ADBB` | Non-best sentiment bars |

Spacing: 4, 8, 12, 16, 24, 32, 48, 64 px. Radius: 6 (controls inside sheets), 10 (inputs,
buttons), 14 (sheets). Shadow: one soft shadow for sheets only.

## Type

IBM Plex Sans (400, 500, 600), served locally, with tabular figures everywhere.
IBM Plex Mono only for code, endpoints and JSON. Scale: 13, 14, 15, 17, 22, 26, 30 px.
Sentence case for all labels; no all-caps eyebrows. Action codes (PASS, QUEUE, ABSTAIN)
keep their API spelling because they are identifiers.

## Action marks

| Action | Shape | Color | Meaning shown to users |
|---|---|---|---|
| ABSTAIN | Diamond | Marigold | Needs a person |
| QUEUE | Square | Brick red | Complaint for the admin queue |
| PASS | Circle | Green | Stored without review |

Shape and text always accompany color, so the meaning survives color blindness and
grayscale printing.

## Information architecture

Four views (Hick's law): **Analyze** (one review), **Batch** (many reviews, table, filters,
CSV export of the results), **Inbox** (this session's decisions by action) and **Integrate**
(API contract, code samples, last real response, model card from `/model`).

## Interaction rules

- Inline validation under the field, with the reason and how to fix it.
- Skeleton loaders while the service answers; the confidence needle and bars animate once
  to show the change. `prefers-reduced-motion` disables all motion.
- `Ctrl + Enter` submits; every control is reachable by keyboard with a visible focus ring.
- Errors say what happened and what to do ("Check that uvicorn is running on port 8000").
- Responsive down to 360 px: one column, scrollable tabs, full-width primary button.
