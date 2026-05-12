---
name: campusai-ui
description: "ui design workflow for CampusAI Advisor. Use for Streamlit UI, Next.js UI, landing pages, dashboards, chat interfaces, upload/index flows, citation cards, student profile forms, and demo polish. Prioritize clarity, trust, source visibility, responsive layout, and portfolio-grade appearance without turning the product into generic AI visual noise."
---

# CampusAI UI

Use this local skill when building or polishing UI for CampusAI Advisor.

The UI should feel like a serious academic AI product, not a random neon chatbot wrapper that escaped from a SaaS template farm.

## Product UI goals

Prioritize:

1. Readability
2. Trust
3. Clear citations
4. Smooth chat flow
5. Obvious upload/index flow
6. Student profile context
7. Clean demo experience
8. Visual polish

## Recommended aesthetic

Default direction:

```text
Academic Aurora Dashboard
```

Use:

- dark or soft neutral background,
- calm blue/teal/violet accent,
- readable cards,
- subtle glow only for emphasis,
- clear hierarchy,
- citation cards that look trustworthy,
- restrained animation.

Avoid:

- generic purple gradient hero sections,
- excessive glassmorphism,
- unreadable low-contrast text,
- cartoonish AI robot mascots,
- decorative effects that hide citations,
- UI that looks more exciting than useful.

## Core screens

### Landing / intro

Must explain in one screen:

- What CampusAI does.
- Who it is for.
- What documents it uses.
- Why citations matter.
- How the demo works.

### Student profile

Fields:

```text
major
academic year
career goal
completed courses
interests
weak areas or learning goals
```

Profile context should be visible enough that the user understands why advice is personalized.

### Document upload / indexing

Must show:

```text
upload area
file list
index button
status: not indexed / indexing / indexed / failed
error message when indexing fails
```

### Chat

Must show:

```text
user question
assistant answer
citations
retrieval/source status
fallback when evidence is missing
```

### Citations

Citation display is not optional.

Each citation should show:

```text
document title
page or section if available
short source excerpt if available
relevance or order indicator if useful
```

## Streamlit MVP guidance

Streamlit is the default MVP UI path unless the user explicitly asks for a different frontend.

For Streamlit:

- Use sidebar for profile and document controls.
- Use main area for chat.
- Use expanders or cards for citations.
- Use session state carefully.
- Keep custom CSS small and readable.
- Do not over-customize Streamlit until the core demo works.

Suggested layout:

```text
Sidebar:
  Student Profile
  Document Upload
  Index Documents
  System Status

Main:
  Title
  Short explanation
  Chat history
  Chat input
  Answer
  Citations
```

## Next.js V2 guidance

For Next.js:

- Use TypeScript.
- Use Tailwind.
- Keep API client isolated.
- Use components for profile panel, chat window, citation card, upload panel, and status badge.
- Use mobile-first layout.
- Avoid complex state management unless needed.

## Visual tokens

Use a consistent token system.

```css
:root {
  --bg: #080b12;
  --surface: #111827;
  --surface-2: #182235;
  --accent: #38bdf8;
  --accent-2: #8b5cf6;
  --text: #eef2ff;
  --text-muted: #94a3b8;
  --border: rgba(255, 255, 255, 0.10);
  --success: #22c55e;
  --warning: #f59e0b;
  --danger: #ef4444;
}
```

## Accessibility and usability

Required:

- Good contrast.
- Keyboard focus states for interactive elements.
- Clear disabled states.
- Loading and error states.
- Mobile-friendly layout.
- Avoid animation that affects readability.

## UI quality checklist

Before calling UI done:

```text
[ ] The user can understand the product in under 10 seconds.
[ ] The user can see profile context.
[ ] Upload/index flow is obvious.
[ ] Chat input is easy to find.
[ ] Citations are visible and credible.
[ ] Missing-source fallback is clear.
[ ] UI works on laptop and mobile widths.
[ ] Empty states are not ugly.
[ ] Loading states exist.
[ ] Error states exist.
[ ] README screenshots or demo script can explain the flow.
```

## Response/reporting format

When finishing a UI task, report:

```text
Screens changed:
Components changed:
States handled:
Verification:
Known UI limitations:
Next polish step:
```
