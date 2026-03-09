## 2026 FRC Climb Stats Scripts

This small project downloads match data from The Blue Alliance (TBA) for the 2026 FRC season and computes:

- **Per-robot climb points** based on the 2026 game rules (auto and endgame tower climbs).
- **Per-team totals** and **how many of each climb type** (auto, Level 1/2/3 endgame) each team achieved.
- **Per-alliance match summaries**, with traversal RP matches highlighted.

Results are written to two CSV files so they can be explored in Excel/Sheets or imported into other tools.

---

## Project structure

- **`week_1_climbs.py`**  
  Main script. It:
  - Uses `TBADataDownloader` to fetch event and match data.
  - Filters events to only include those that finished at least one full day ago.
  - Scores each robot’s climbs using the 2026 rules:
    - Auto climb: **15 points** per robot that climbed in auto.
    - Endgame climb: **10 / 20 / 30 points** for Level 1 / 2 / 3.
  - Tracks, per team:
    - Total climb points.
    - Count of auto climbs.
    - Count of Level 1 / Level 2 / Level 3 endgame climbs.
  - Builds a list of match descriptions (one per alliance) including:
    - Event key, match ID, alliance color.
    - Teams on the alliance.
    - Auto + endgame tower points.
    - Whether a traversal RP was achieved.
  - Prints to the console:
    - Only **matches where traversal RP was achieved**.
    - Only the **top 10 teams** by total robot climb points.
  - Writes CSV files:
    - `match_climbs.csv` – one row per alliance in each match.
    - `team_climbs.csv` – one row per team with totals and climb counts.

- **`downloader.py`**  
  Helper module that wraps all calls to The Blue Alliance API and handles response caching:
  - `get_completed_event_keys(year)`  
    Fetches all events for the year and returns only those whose end date is at least one full day in the past.  
    Also caches each event as `cachedResponses/event_<event_key>.json`.
  - `get_event_matches(event_key)`  
    Returns all matches for an event, using a local cache file `cachedResponses/matches_<event_key>.json` when available.

- **`cachedResponses/`**  
  Folder created automatically to store JSON responses from TBA:
  - `event_<event_key>.json`
  - `matches_<event_key>.json`
  This folder is git-ignored.

- **`secrets.py`**  
  Small file that must define your TBA API key:

  ```python
  TBA_API_KEY = "your_real_api_key_here"
  ```

  This file is in `.gitignore` so you don’t accidentally share your key.

---

## Setup (for students new to Python)

You will need:

- **Python 3.10+** installed.
- A **TBA API key** from The Blue Alliance.

### 1. Install Python

Download and install Python from the official site:

- [Install Python](https://www.python.org/downloads/)

When installing on Windows, **check the box** that says “Add Python to PATH” during setup.

You can check your install in a terminal (PowerShell or Command Prompt) with:

```bash
python --version
```

or sometimes:

```bash
py --version
```

### 2. Create and activate a virtual environment (venv)

A *virtual environment* keeps the Python packages for this project separate from other projects on your computer.

Official docs:  
[Python venv tutorial](https://docs.python.org/3/tutorial/venv.html)

From the project folder (`frc_2026_tba_scripts`):

```bash
python -m venv .venv
```

Then activate it:

- **On Windows (PowerShell)**:

  ```bash
  .venv\Scripts\Activate.ps1
  ```

- **On Windows (Command Prompt)**:

  ```bash
  .venv\Scripts\activate.bat
  ```

When it works, you should see `(.venv)` at the beginning of your terminal prompt.

To deactivate later:

```bash
deactivate
```

### 3. Install Python dependencies

This project uses `pip` to install packages listed in `requirements.txt`.

Official docs:  
[Installing Python packages with pip](https://pip.pypa.io/en/stable/user_guide/)

With your virtual environment **activated** and your terminal in the project folder:

```bash
pip install -r requirements.txt
```

This will install:

- `requests` – used to talk to The Blue Alliance API.

### 4. Add your TBA API key

Create a file named `secrets.py` in the project folder with:

```python
TBA_API_KEY = "your_real_api_key_here"
```

You can create a TBA API key by logging into The Blue Alliance and going to your account settings.

---

## Running the script

With your virtual environment activated and dependencies installed:

```bash
python week_1_climbs.py
```

What happens:

- The script asks TBA for all 2026 events.
- It keeps only events whose end date is at least one full day in the past.
- For each completed event, it:
  - Fetches matches (using the cache when possible).
  - Scores robot climbs and updates team totals and climb counts.
  - Records a summary line for any alliance that scored climb points.
- At the end it:
  - Prints all **matches with a traversal RP** to the console.
  - Prints the **top 10 teams by total robot climb points**.
  - Writes/overwrites two CSV files in the project folder:
    - `match_climbs.csv`
    - `team_climbs.csv`

You can open the CSV files in:

- Excel
- Google Sheets
- LibreOffice Calc
- Or any data analysis tool you prefer.

---

## Notes and tips

- If you change the year, update the `YEAR` constant in `week_1_climbs.py`.
- If the script seems to be using old data for matches, you can delete files in `cachedResponses/` and run again. (Event lists are always fetched fresh.)
- If you get errors about `requests` not being found, make sure:
  - Your virtual environment is activated.
  - `pip install -r requirements.txt` has been run without errors.

