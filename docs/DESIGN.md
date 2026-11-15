# SentiTriage-ES design system

The interface has one job: show what the agent decided and why, so a person can trust it or
take over. Its identity comes from the product's core idea: **the agent knows when not to
decide**. The threshold τ is the signature element and owns the only accent color.

## Brief

| | |
|---|---|
| **Users** | Administrators of a business that receives written feedback in Spanish (first case: a Colombian restaurant), and developers who connect that business's system to the API. |
| **Problem** | Reading every review is not possible, and an automatic label that is silently wrong makes the business miss complaints. The interface must show what the agent decided, how sure it was, and when a person must take over. |
| **Style** | Calm, precise, trustworthy. Closer to a professional tool than to a marketing page. |
| **Avoid** | Purple AI gradients, decorative badges above headings, random italics, identical cards for everything, all-caps eyebrows, monospace for ordinary labels, colors that mix sentiment with decisions. |
| **Stack** | One HTML file with vanilla CSS and JavaScript, served by FastAPI. No build step, no external requests, fonts served locally. |
| **Dials (1–10)** | Variance 3 (sober, one signature element). Motion 2 (only to confirm a result). Density 5 (tables and metrics, with room to read). |

## Principles

1. **Decision first.** The verdict (action + plain-language title + reason) is the largest
   element on screen. Probabilities and confidence support it; they never compete with it.
2. **Decisions and sentiment never share a visual language.** Actions (PASS, QUEUE,
   ABSTAIN) use color *and* shape. Sentiment classes (negative, neutral, positive) are what
   the model believes, so they are drawn in ink: the best guess dark, the rest grey.
3. **One accent.** Marigold marks the threshold τ and the abstention zone, and nothing else.
4. **Real data only.** Every number on screen comes from the API (`/classify`,
   `/classify/batch`, `/model`). The sample texts are real comments (Correa, 2019, CC BY 4.0).
5. **Group by space, not by boxes.** Sheets hold inputs, tables and the decision; inside them,
   content is structured by type size and rules, not by nested boxes. The decision panel is the
   widest sheet (7 of 12 columns) and has the most padding (32 px), so it reads as the result.

## Tokens

| Token | Value | Use |
|---|---|---|
| `--ink` | `#13213A` | Text, app bar, primary button, best-guess bar |
| `--ink-2` | `#3B4657` | Secondary text: leads, help, reasons (8.4:1 on `--bg`) |
| `--ink-3` | `#4F5A6B` | Tertiary text: sources, hints, notes (6.1:1 on `--bg`) |
| `--bg` | `#EEF1F0` | Page background (cool mist) |
| `--surface` | `#FFFFFF` | Sheets, lanes, dialog |
| `--accent` | `#E9A21B` | Threshold τ, abstention zone, ABSTAIN mark |
| `--abstain` | `#8A5300` | ABSTAIN text (meets 4.5:1 on white) |
| `--queue` | `#B2302A` | QUEUE mark and text |
| `--pass` | `#1D6B52` | PASS mark and text |
| `--sent-other` | `#A3ADBB` | Non-best sentiment bars |

Spacing: 4, 8, 12, 16, 24, 32, 48, 64 px; the one exception is the 40 px gap between the input
and the decision in Analyze. Radius: 6 (controls inside sheets), 10 (inputs, buttons), 14
(sheets). Shadow: one soft shadow for sheets only.

## Type

IBM Plex Sans (400, 500, 600), served locally, with tabular figures everywhere.
IBM Plex Mono only for code, endpoints and JSON.

Five sizes, in rem, and no others:

| Token | Size | Use |
|---|---|---|
| `--fs-decision` | 2.125rem (34 px) | The verdict title and the batch counts: the decision is the largest text |
| `--fs-title` | 1.875rem (30 px) | View title (h1); verdict and counts on phones |
| `--fs-sub` | 1.125rem (18 px) | Section subtitles, panel and lane titles, the quoted review, brand |
| `--fs-body` | 1rem (16 px) | Body text, field labels, buttons, sentiment classes |
| `--fs-small` | 0.875rem (14 px) | Labels, help, tables, chips, code, notes, footer |

Paragraphs stay between 50 and 75 characters per line (`max-width` in `ch`).
Sentence case for all labels; no all-caps eyebrows. Action codes (PASS, QUEUE, ABSTAIN)
keep their API spelling because they are identifiers; in the verdict the code sits on the
same line as the title, as an outlined tag, not above it.

## Units and layout

- **rem for text.** Every font size uses one of the five tokens above, so the interface follows
  the text size the user sets in the browser.
- **% and vw for layout.** The page (app bar, main and footer) uses side margins of
  `clamp(24px, 4vw, 56px)`, about 92 % of the viewport, and the content stops growing at
  1480 px. Grids use fractions (`minmax(0, 5fr) minmax(0, 7fr)`), never fixed widths.
- **px for borders, shadows, radii and spacing**, which should not scale with the text.
- **Touch targets of at least 44 × 44 px on phones** (≤ 760 px): navigation, the primary
  button, the EN/ES selector and the sample chips. On desktop the EN/ES selector and the chips
  can be compact (30 and 40 px), because they are used with a pointer.
- **Above the fold at 1536 × 695** (a 1080p laptop at 125 % scaling with the browser bar): the
  view header is compact (title and one-line lead), so the input, the primary button and the
  verdict are visible without scrolling.

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

## Geometry

Nested corners follow *inner radius = outer radius − padding* when the inner element touches
the outer corner: the Copy button (4 px) inside the code header (10 px radius, 6 px padding);
the language buttons (7 px) inside their 10 px group with 2 px padding and a 1 px border.
Where padding is larger than the outer radius (sheets with 24 px padding), inner elements use
the control radius (10 px) and do not touch the corner.

## Language

The interface is bilingual (EN and ES) with a selector in the app bar. The first visit follows
the browser language; the choice is remembered in the browser.

- Spanish is neutral Colombian Spanish with informal *tú*, the same verbs as the English
  version ("Clasificar reseña" / "Classify review") and the same term for each concept
  everywhere: *reseña*, *umbral τ*, *confianza calibrada*, *clase más probable*, *cola del
  administrador*.
- Sentiment classes agree with *reseña*: *negativa*, *neutral*, *positiva*.
- Numbers on screen follow the language (0,56 and 2.000 in Spanish; 0.56 and 2,000 in
  English). Code, JSON, the API and the exported CSV keep the API format.
- Action codes (PASS, QUEUE, ABSTAIN), endpoints and JSON keys are never translated: they are
  identifiers of the API.
- Customer reviews are always shown as written, marked `lang="es"`.

## Interaction rules

- Inline validation under the field while typing (length limits); an empty field is reported
  only when sending, so the user is not scolded before starting.
- Skeleton loaders while the service answers; the confidence needle and bars animate once
  to show the change. `prefers-reduced-motion` disables all motion.
- `Ctrl + Enter` submits; every control is reachable by keyboard with a visible focus ring.
- Errors say what happened and what to do ("Check that uvicorn is running on port 8000").
- Responsive down to 360 px: one column, scrollable tabs, full-width primary button; on one-
  column layouts the page scrolls to the decision after classifying.
- Headings use `text-wrap: balance` and paragraphs `text-wrap: pretty`.
