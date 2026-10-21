# Storyverse Team Schedule 团队排班

Single-file web app for entering the team's daily tasks, with per-team deadline warnings:

| Team | Deadline (same day) |
|---|---|
| China 中国组 | 18:00 Asia/Shanghai |
| US 美国组 | 10:00 America/Los_Angeles |
| London 伦敦组 | 18:00 Asia/Shanghai |
| Intern 实习生 | 10:00 America/Los_Angeles |

Teams, deadlines, and members are editable in Settings (any number of teams). Defaults live at the top
of the script in `template.html` (`TEAM_DEFAULTS`, `TEAMS_DEFAULT`); bump `DATA_VERSION` / `SETTINGS_VERSION`
and add a migration when changing defaults so existing browsers pick them up without losing tasks.

Open `index.html` in a browser. Data saves to the browser's local storage; use Export/Import JSON to move it between devices.

Rebuild from the Google Sheet: download it to `../sheet.csv`, then run `python3 parse_sheet.py && python3 build.py`.
Test: `python3 -m http.server 8765` in this folder, then `python3 test.py` (Playwright + Chrome; `?now=<ISO>` simulates time).

## Cloud sync (optional)
Click **登录** and paste a GitHub token with Contents read/write on the private data repo
(`SYNC` constant in `template.html`, currently `dora11111111/storyverse-schedule-data`, file `schedule.json`).
The token is kept in this browser's localStorage under `sv_schedule_token` (separate from the payroll app).
Not signed in = local-only, exactly as before.
