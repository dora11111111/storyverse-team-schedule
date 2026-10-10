# Storyverse Team Schedule 团队排班

Single-file web app for entering the team's daily tasks, with deadline warnings
(China team: 6:00 PM Asia/Shanghai, US team: 10:00 AM America/Los_Angeles).

Open `index.html` in a browser. Data saves to the browser's local storage; use Export/Import JSON to move it between devices.

Rebuild from the Google Sheet: download it to `../sheet.csv`, then run `python3 parse_sheet.py && python3 build.py`.
