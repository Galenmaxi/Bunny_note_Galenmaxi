# 🐰 Bunnynote — Project Handoff

> **For the next Claude agent:** Read this entire document before touching any code. The actual code is always the source of truth — verify against `index.html` before acting on anything here.

---

## 📌 What Is This Project?

**Bunnynote** is a personal productivity web app built for **Galen Maximilian** (GalenMaxi). It started as a Notion alternative for someone who found Notion too complex. The aesthetic is **NewJeans/NJZ K-pop Y2K** — denim, bunnies, polaroid cards, cassette tapes, pastel Y2K colors, Windows XP-style background.

**Live URL:** `https://bunnynote-maxi.netlify.app`  
**Owner:** Galen Maximilian (`maximiliangalen@gmail.com`)  
**Built into:** Single HTML file deployed on Netlify

---

## 🛠️ Tech Stack

| Layer | Tool | Details |
|-------|------|---------|
| Frontend | HTML + Tailwind CSS (CDN) | Single `index.html` file, ~847KB |
| Fonts | Google Fonts | Bricolage Grotesque, Plus Jakarta Sans, Nunito Sans |
| Icons | Material Symbols Outlined | Via Google CDN |
| Database | Supabase (PostgreSQL) | REST API via fetch, no SDK |
| Hosting | Netlify | Drag & drop zip deploys |
| AI Feature | ~~Anthropic Claude API~~ | **REMOVED** — Galen doesn't use it (cost concern) |
| Auth | None | No login, all Supabase data is public (RLS allow-all) |

---

## 🗄️ Supabase

**Project URL:** `https://edyzybrukvleundcttzw.supabase.co`  
**Anon Key:** stored in `index.html` as `SB_KEY` constant  
**RLS:** Enabled on all tables with `allow all` policy

### Tables
```sql
tasks             (id, text, cat, priority, done, recurring, created_at)
notes             (id, title, content, folder, tags, deadline, domain, status, created_at)
goals             (id, title, current_val, target_val, unit, deadline, created_at)
habits            (id, name, created_at)
habit_completions (id, habit_id, completed_date, UNIQUE(habit_id, completed_date))
projects          (id, name, cat, created_at)
settings          (key, value)  -- stores: name, mood, focus, reflection, cats
```

### Columns added (verify these exist in your Supabase):
```sql
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurring TEXT DEFAULT '';
ALTER TABLE notes ADD COLUMN IF NOT EXISTS domain TEXT;
ALTER TABLE notes ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'due';
ALTER TABLE notes ADD COLUMN IF NOT EXISTS deadline DATE;
```

---

## 🚀 Netlify Setup

**Site name:** `bunnynote-maxi`  
**Deploy method:** Zip the `bunnynote-site` folder (NOT the outer `bunnynote-deploy` folder), drag to Netlify.

### Deployed zip structure:
```
index.html                     ← entire app
netlify.toml                   ← build config + redirect
netlify/
  functions/
    brief.js                   ← AI function (still exists but unused)
```

### netlify.toml:
```toml
[build]
  command = ""
  publish = "."
  functions = "netlify/functions"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/api/brief"
  to = "/.netlify/functions/brief"
  status = 200
```

### Environment Variables (Netlify dashboard):
- `ANTHROPIC_API_KEY` — still set but no longer used (AI feature removed from frontend)

---

## 📱 Pages & Features

### Navigation (bottom nav bar — fixed, always visible)
| Nav Item | Page ID | Status |
|----------|---------|--------|
| 🏠 Home | `page-home` | ✅ Built |
| 📼 Notes | `page-notes` | ✅ Built |
| ✅ Tasks | `page-tasks` | ✅ Built |
| ⭐ Goals | `page-goals` | ✅ Built |
| 📅 Calendar | `page-calendar` | ✅ Built |
| ⏱️ Timer | `page-pomodoro` | ✅ Built |
| 📊 Stats | `page-stats` | ✅ Built |

### Home Page
- `annyeong, Galen 🐰` greeting (name pulled from settings)
- ~~AI Daily Brief~~ — **REMOVED**
- 📌 Today's Focus (3 priority cards, editable via modal)
- ⚡ Upcoming Deadlines widget (next items from notes with deadlines)
- 😊 Vibe Check (mood selector, saves to settings table)
- 🔥 Habits (hearts streak display)
- 📊 Today's Progress bar (tasks done/total)
- 🃏 Recent Scraps (last 2 notes as polaroid cards)
- 🎞️ Active Tapes (projects list)
- Quick nav buttons → Focus, Calendar, Stats
- Lightning McQueen quote cassette tape (hardcoded)

### Tasks Page
- 3 categories: Academic Goals / Creative Projects / Life & Bunnies
- Category names **renameable** via Settings
- Drag & drop to reorder within category
- Priority: ♨️ High / ✨ Mid / ♡ Low
- Recurring: Once / 🔁 Daily / 📅 Weekly
- Filter: All / Pending / Done
- Bunny hop animation on checkbox complete
- Recurring badge shown on task cards
- **Recurring tasks properly reset** across sessions (see bug fixes below)

### Notes Page
- **Card view** (default) — polaroid-style grid, drag to reorder
- **Table view** (toggle) — Notion-style deadline table:
  - Columns: Name (with `›` chevron to open view modal), Domain, Due Date, Days Left, Status, Actions
  - Sorted by deadline ascending
  - Status: 🔴 due / ⚪ tentative / ✅ done / 📂 open
  - **Overdue rows** get a red left border (`note-overdue-row`) when `deadline < today && status !== 'done'`
  - Hover `✓` button to mark a note done; hover `↩` button in Done tab to restore
  - Delete `✕` button visible on row hover
- Folder tabs: All / 📘 School / 💼 Work / 🐰 Personal / 💡 Ideas / ✅ Done
  - **All / folder tabs** exclude `status === 'done'` notes
  - **✅ Done tab** shows only `status === 'done'` notes
- Rich text editor (bold, italic, underline, bullet, numbered, checkbox)
- Note view modal (tap card or chevron to read full content)
  - View modal has **✅ Done / ↩ Restore** button that patches status in Supabase then re-renders
- `markNoteDone(id)` — patches `status: 'done'`, updates cache, re-renders notes + home + deadlines
- `restoreNote(id)` — patches `status: 'open'`, updates cache, re-renders notes + home + deadlines

### Goals Page
- Goal cards with cassette-style progress bars (+1/+5/-1 buttons)
- 7-day habit tracker grid (dot matrix, tap to mark days)
- Weekly reflection diary (saves to settings table)

### Calendar Page
- Monthly calendar view
- Color-coded: 🔵 note deadlines, 🟡 goal deadlines
- Tap a day to see what's scheduled
- Navigate months with ‹ ›

### Pomodoro Timer Page
- 3 modes: 🍅 Focus (25min) / ☕ Short Break (5min) / 🌸 Long Break (15min)
- Animated SVG ring countdown
- Link a task to session
- Session counter (resets daily via localStorage)
- Ding sound on completion (Web Audio API)

### Stats Page
- Summary cards: Tasks Done, Total Notes, Goals Done, Best Streak
- Tasks by category progress bars
- Notes by folder progress bars
- Habit streaks
- Goals overview
- **Custom background uploader** (saves base64 to `bn_customBg` in localStorage)

### Settings Modal
- Rename yourself (updates greeting)
- Rename 3 task categories
- NewJeans member accent color picker — **now works** (see color themes below)
- Clear all data button

---

## 🎨 Design System

### Colors (Tailwind extended config)
```
primary:             #42617d   (denim blue)
secondary:           #864d61   (mauve pink)
primary-container:   #a7c7e7
secondary-container: #fdb5cc
background:          #f8f9fa
on-surface:          #191c1d
```

### NewJeans Color Themes (Settings → pick a member)
The `setAccent(name, hex)` function injects a `<style id="theme-override">` tag that overrides box shadows, nav highlight, progress bars, habit dots, and card shadows. **Does NOT persist between sessions** (by design — always loads default colors on startup).

| Member | Key | Accent | Shadow |
|--------|-----|--------|--------|
| Minji 🌸 | `pink` | `#fab3ca` | `#42617d` |
| Hanni 💙 | `blue` | `#aacaea` | `#5a4072` |
| Danielle 🌿 | `mint` | `#b8e8d8` | `#2d7a5f` |
| Haerin 💜 | `lavender` | `#d4b8e8` | `#6b3d9b` |
| Hyein ⭐ | `butter` | `#FFF9C4` | `#b89a00` |

### Key CSS Classes
```
.sticker-border        — 2px solid border + Y2K offset box shadow
.polaroid-card         — white card with thick bottom border
.task-card             — glassmorphism card, draggable
.note-card             — draggable note card
.retro-cd-label        — pill-shaped category header
.rich-editor           — contenteditable rich text area
.rich-toolbar          — formatting toolbar above editor
.recurring-badge       — blue pill badge on recurring tasks
.habit-dot             — circular habit tracker dot
.progress-bar-bg       — rounded progress bar container
.progress-bar-fill     — animated gradient fill (pink→blue)
.modal-overlay         — full screen dimmed backdrop (IMPORTANT: see CSS fix below)
.modal-overlay:not(.hidden) — display:flex only when visible (critical fix)
.float-anim            — floating animation for decorative elements
.streak-bunny          — bunny that runs across screen on streak milestone
.confetti-piece        — falling confetti on streak celebration
.ppg-loader            — loading screen character animation (ppgBounce keyframe)
.note-title-cell       — flex container for title + chevron in table row (height: 52px)
.note-title-text       — ellipsis-clipped title text (flex:1, min-width:0)
.note-chevron-btn      — round › button, hidden until row hover, opens view modal
.note-overdue-row      — red left border (3px solid #ef4444) on overdue table rows
.note-done-btn         — round ✓/↩ button, hidden until row hover; .is-done (green) or .is-restore (grey)
```

### Loading Screen
- Shows **Haerin's photo** (`NewJeans HAERIN.jpg`) embedded as base64 in `PPG_LOADER_SRC` constant
- Animated with `ppgBounce` keyframe (bouncy tilt + float)
- Falls back to 🐰 emoji if image fails

### Background
- Default: NJZ Y2K Windows desktop image (base64 embedded in CSS `body { background-image }`)
- Custom: User uploads via Stats page → saved to `bn_customBg` localStorage
- When custom bg is set, `loadCustomBg()` applies a `rgba(248,249,250,0.35)` overlay for readability

### Card Opacity
Cards use `backdrop-blur-xl` + semi-transparent backgrounds. Opacities were increased for readability:
- `bg-surface-container-lowest` → `/95` or `/97`
- `bg-surface-container-low` → `/97`
- `bg-white` → `/95`

### Header
- **Fixed** (not sticky) — `fixed top-0 left-0 right-0 z-50`
- `.page.active` has `padding-top: 56px` so content doesn't hide under header

### Fonts
- Headlines: `Plus Jakarta Sans` (700)
- Labels/caps: `Bricolage Grotesque` (700/800)
- Body: `Nunito Sans` (400/600)

---

## 💾 Data Architecture

### Supabase (cloud, all devices)
Tasks, Notes, Goals, Habits, Habit Completions, Projects, Settings

### localStorage (this device only)
```
bn_notifications     — notification history array
bn_quoteIdx          — current quote rotation index
bn_pomSessions       — today's pomodoro session count
bn_pomDate           — date string for daily pomodoro reset
bn_customBg          — base64 custom background image
bn_recurring_done    — {taskId: {text,cat,priority,recurring,doneAt}} for cross-session recurring resets
bn_theme             — saved accent theme name (written by setAccent but NOT read on startup)
```

Note: `bn_lastBrief` was removed (AI feature gone).

### In-memory cache object
```javascript
cache = {
  tasks, notes, goals, habits, projects,  // arrays from Supabase
  habitDots,    // {habitId: {dateStr: bool}} from habit_completions
  name,         // from settings table
  mood,         // from settings table
  focus,        // JSON array from settings table
  reflection,   // from settings table
  cats,         // {academic, creative, life} category names
}
```

---

## 🔄 Recurring Tasks (Fixed)

**Old (broken):** Used `setTimeout(86400000)` — timer died when browser closed.

**New (fixed):** When a recurring task is marked done, saves to `bn_recurring_done` localStorage:
```js
{ taskId: { text, cat, priority, recurring, doneAt: ISO string } }
```
On every app load, `checkRecurringResets()` runs and creates fresh Supabase tasks for any daily (≥1 day old) or weekly (≥7 days old) completed recurring tasks, then clears them from localStorage.

---

## 🐛 Bugs Fixed

### May 2026 Session
1. **Modal overlay always visible** — Critical CSS bug: `.modal-overlay { display: flex }` was overriding Tailwind's `.hidden { display: none }`. Fixed: `.modal-overlay:not(.hidden) { display: flex }`. **Never revert.**

2. **Recurring tasks not resetting** — `setTimeout(24h)` died on browser close. Fixed with localStorage tracking + `checkRecurringResets()` on load.

3. **`setAccent()` did nothing** — The function only showed a toast. Now properly applies CSS overrides.

4. **Stray byte before DOCTYPE** — PowerShell encoding operations introduced a `?` character before `<!DOCTYPE html>`, triggering browser quirks mode. Fixed by stripping the byte.

5. **UTF-8 BOM added by PowerShell** — `WriteAllText` with `Encoding.UTF8` adds a BOM. Fixed: use `WriteAllBytes` starting at offset 3.

6. **Orphaned JS code from regex removal** — PowerShell regex removal of `initBrief()` left orphaned `} catch { }` lines outside any function, causing a script-wide syntax error. Fixed manually with Edit tool.

7. **Encoding corruption** — Multiple rounds of `Get-Content` (ANSI) + `Set-Content -Encoding utf8` corrupted emoji/special chars. Fixed by CP1252 round-trip.

### June 2026 Session
8. **`renderRecentNotes()` showed done notes on home page** — `cache.notes.slice(0, 2)` pulled the first 2 notes from full cache without filtering by status. Fixed: `.filter(n => n.status !== 'done').slice(0, 2)`.

---

## ⚠️ Critical Rules for Future Agents

1. **Never use PowerShell `Get-Content` / `Set-Content` on this file** — it corrupts UTF-8 emoji. Use `[System.IO.File]::ReadAllText(path, UTF8)` and `[System.IO.File]::WriteAllBytes(path, bytes)` (NOT `WriteAllText` which adds BOM).

2. **Never use PowerShell regex to remove large JS blocks** — `(?s).*?` is too fragile. Use the Edit tool with exact text matching instead.

3. **Never revert `.modal-overlay:not(.hidden)`** — The original `.modal-overlay { display: flex }` was the root cause of the search overlay being permanently visible. The fix is mandatory.

4. **Never use `setTimeout` for recurring task resets** — The localStorage approach is the correct fix.

5. **Always verify first bytes** — After any PowerShell file operation, check `$bytes[0..2]` to ensure no BOM (EF BB BF) and no stray chars before `<!DOCTYPE`.

6. **Deploy zip = `bunnynote-site` contents** — NOT the outer `bunnynote-deploy` folder. Run `Compress-Archive -Path "$src\*"` not `-Path $src`.

---

## 📋 What's NOT Built Yet

| Feature | Priority | Notes |
|---------|----------|-------|
| Login / Auth | High | No auth, all Supabase data is public |
| Dark mode | Medium | CSS vars ready, just needs a toggle |
| Export data (CSV/PDF) | Low | Useful for notes/deadlines |
| Task due dates | Medium | Tasks have no deadline field, only notes do |
| Push notifications | Low | Needs PWA service worker |
| Share note via link | Low | Needs auth first |

---

## 🔍 Agent Verification Checklist

Run these before making ANY changes:

```
1. File starts with <!DOCTYPE (no BOM, no stray chars)
   → Check: first bytes should be 3C 21 44 4F 43

2. Modal overlay CSS fix exists
   → Search: .modal-overlay:not(.hidden)

3. Header is fixed (not sticky)
   → Search: fixed top-0 left-0 right-0

4. .page.active has padding-top: 56px
   → Search in CSS block

5. AI feature is fully removed
   → Search: generateBrief (should be 0 results)
   → Search: ai-brief (should be 0 results)

6. Recurring tasks use localStorage (not setTimeout)
   → Search: bn_recurring_done
   → Search: checkRecurringResets

7. All 9 modals have class="modal-overlay hidden"
   → modal-settings, modal-focus, modal-habits, modal-note-new,
     modal-note-view, modal-goal-new, modal-project,
     modal-notifications, search-overlay

8. Critical functions present
   → showPage, openModal, closeModal, init, renderHome,
     renderTasks, renderNotes, renderGoals, renderCalendar,
     pomodoroStartStop, renderStats, checkRecurringResets,
     loadCustomBg, checkDueBanner, markNoteDone, restoreNote,
     filterNotes, renderRecentNotes, renderUpcomingDeadlines

9. Supabase constants present
   → SB_URL = 'https://edyzybrukvleundcttzw.supabase.co'
   → SB_KEY = 'eyJ...'

10. No orphaned code between functions
    → Look for lone } catch { } or } lines outside function bodies
    → Especially between renderUpcomingDeadlines and checkDueBanner
```

---

## 💬 About Galen

- Student (taking DAA, C++, DSA, NLP, OS, Deep Learning)
- Samsung phone user, ASUS laptop, Chrome browser
- Deployed on `bunnynote-maxi.netlify.app`
- Loves NewJeans/NJZ (especially Haerin 🐰)
- Favorite quote: *"I just never thought I couldn't." — Lightning McQueen ⚡*
- **Does not use AI features** — cost concern, no Anthropic API key budget
- Prefers all instructions given at once, not step by step
- App name: **Bunnynote** 🐰

---

*Last updated: June 2026 — updated from Claude Code session*  
*May 2026: modal fix, recurring fix, themes, loading screen, header fix, AI removal, UI polish*  
*June 2026: Notes table redesign (chevron-to-modal, removed Notes column), Done/Archive tab for notes, overdue row highlighting, renderRecentNotes bug fix*
