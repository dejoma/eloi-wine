# Corkscrew 🍷

**Corkscrew** is a tool that automatically downloads wine inventory files from ~40 top wine merchants and organises them into a single, clean spreadsheet you can open in Excel or Google Sheets.

No technical knowledge is needed to *use* it — this guide will walk you through every single step, from installing Python to running your first download, even if you have never typed a command into a computer before.

---

## Table of Contents

1. [What does Corkscrew do?](#what-does-corkscrew-do)
2. [What is a "terminal" and why do I need one?](#what-is-a-terminal)
3. [Installation — macOS](#installation--macos)
4. [Installation — Windows](#installation--windows)
5. [Running Corkscrew for the first time](#running-corkscrew-for-the-first-time)
6. [Command reference](#command-reference)
   - [corkscrew run](#corkscrew-run)
   - [corkscrew status](#corkscrew-status)
   - [corkscrew list](#corkscrew-list)
   - [corkscrew merge](#corkscrew-merge)
7. [Understanding the output on screen](#understanding-the-output-on-screen)
8. [Where are my files?](#where-are-my-files)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## What does Corkscrew do?

Each wine merchant publishes their stock as a file (Excel spreadsheet, CSV, or JSON). Corkscrew:

1. Downloads those files automatically from ~40 merchants at once.
2. Converts every file into a single, standardised format (CSV).
3. Merges all merchants into one master spreadsheet: `data/master/master.csv`.

You can then open that file in Excel or Google Sheets to search, filter, and compare wines across all merchants.

---

## What is a "terminal"?

A **terminal** (also called a *command prompt* or *shell*) is a text-based way to talk to your computer. Instead of clicking icons, you type short commands and press **Enter**.

It looks like this:

```
Last login: Mon Feb 23 10:00:00 on ttys001
dennis@Macbook ~ %  _
```

The blinking cursor is waiting for you to type something. Don't worry — you can't break anything by typing the wrong command. The worst that can happen is an error message.

---

## Installation — macOS

### Step 1 — Open the Terminal

1. Press **⌘ Command + Space** to open Spotlight Search.
2. Type `Terminal` and press **Enter**.
3. A window with white or black background will open. That is your terminal.

### Step 2 — Check if Python is installed

Type the following and press **Enter**:

```
python3 --version
```

You should see something like:

```
Python 3.13.0
```

The number must be **3.11 or higher**. If it is lower (e.g. `Python 2.7`) or you see `command not found`, go to Step 3. Otherwise, skip to Step 4.

### Step 3 — Install Python (only if needed)

1. Open your web browser and go to **https://www.python.org/downloads/**
2. Click the big yellow **"Download Python 3.x.x"** button.
3. Open the downloaded `.pkg` file.
4. Follow the installer: click **Continue → Continue → Agree → Install**.
5. Enter your Mac password if asked.
6. Once it finishes, go back to the terminal and run `python3 --version` again to confirm.

### Step 4 — Download Corkscrew

**Option A — If you received a zip file:**

1. Double-click the zip file. It will create a folder called `eloi-wine` (or similar).
2. Move that folder somewhere you'll remember, e.g. your Desktop or Documents.
3. In the terminal, type `cd ` (with a space after), then **drag the folder** from Finder into the terminal window. The path will be filled in automatically. Press **Enter**.

   Example of what it looks like after dragging:
   ```
   cd /Users/yourname/Desktop/eloi-wine
   ```

**Option B — If you are cloning from git:**

```
git clone https://github.com/yourname/eloi-wine.git
cd eloi-wine
```

### Step 5 — Create a virtual environment

A virtual environment is an isolated space where Corkscrew's dependencies are installed without affecting the rest of your computer.

```
python3 -m venv .venv
```

This creates a hidden folder called `.venv` in your project directory. You only need to do this once.

### Step 6 — Activate the virtual environment

```
source .venv/bin/activate
```

You will notice the terminal prompt now shows `(.venv)` at the start:

```
(.venv) dennis@Macbook eloi-wine %
```

> **Important:** You need to run this activation command every time you open a new terminal window before using Corkscrew.

### Step 7 — Install dependencies

```
pip install -e ".[dev]"
```

This installs Corkscrew and all the libraries it needs. You will see a lot of text scroll past — that is normal. Wait for it to finish (it may take 1–3 minutes).

When it is done you will see something like:

```
Successfully installed corkscrew-0.1.0 ...
```

### Step 8 — Verify the installation

```
corkscrew --help
```

You should see:

```
Usage: corkscrew [OPTIONS] COMMAND [ARGS]...

  Corkscrew — Wine Merchant Inventory Scraper

Options:
  --help  Show this message and exit.

Commands:
  list    List all configured merchants.
  merge   Merge all latest normalized CSVs into a master file.
  run     Download and normalize wine inventory from merchants.
  status  Show last run status for all merchants.
```

Congratulations — Corkscrew is installed! Jump to [Running Corkscrew for the first time](#running-corkscrew-for-the-first-time).

---

## Installation — Windows

### Step 1 — Open PowerShell

PowerShell is the modern command-line tool on Windows.

1. Press the **Windows key** (the one with the Windows logo, between Ctrl and Alt).
2. Type `PowerShell` and click **Windows PowerShell** (or **Terminal** on Windows 11).
3. A blue (or dark) window will open. That is your terminal.

### Step 2 — Check if Python is installed

Type the following and press **Enter**:

```
python --version
```

You should see something like:

```
Python 3.13.0
```

The number must be **3.11 or higher**. If it says `Python 2.7`, or you see an error, go to Step 3.

> **Windows Store prompt?** If a window pops up suggesting to install Python from the Microsoft Store, close it and follow Step 3 instead — the Store version can sometimes cause issues.

### Step 3 — Install Python (only if needed)

1. Open your web browser and go to **https://www.python.org/downloads/windows/**
2. Click the top link for the latest **Python 3.x.x** release.
3. Scroll down and click **Windows installer (64-bit)**.
4. Open the downloaded `.exe` file.
5. ⚠️ **IMPORTANT**: On the very first screen, check the box that says **"Add Python to PATH"** before clicking Install Now. If you miss this, Python won't work from the terminal.
6. Click **Install Now** and wait for it to finish.
7. Click **Close**.
8. Close and re-open PowerShell, then run `python --version` again.

### Step 4 — Download Corkscrew

**Option A — If you received a zip file:**

1. Right-click the zip file and choose **Extract All...**.
2. Extract it to somewhere memorable, e.g. `C:\Users\YourName\Documents\eloi-wine`.
3. In PowerShell, navigate to that folder:
   ```
   cd "C:\Users\YourName\Documents\eloi-wine"
   ```
   Replace `YourName` with your actual Windows username. You can find it by typing `echo $env:USERNAME`.

**Option B — If you are cloning from git (requires Git for Windows):**

```
git clone https://github.com/yourname/eloi-wine.git
cd eloi-wine
```

> **Don't have Git?** Download it from https://git-scm.com/download/win and run the installer with all defaults.

### Step 5 — Create a virtual environment

```
python -m venv .venv
```

### Step 6 — Activate the virtual environment

```
.venv\Scripts\Activate.ps1
```

You will see `(.venv)` at the start of your prompt:

```
(.venv) PS C:\Users\YourName\Documents\eloi-wine>
```

> **Permission error?** If you see *"running scripts is disabled on this system"*, run this command first:
> ```
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then try the activation command again.

> **Important:** You need to run the activation command every time you open a new PowerShell window.

### Step 7 — Install dependencies

```
pip install -e ".[dev]"
```

Wait for it to finish — it may take 1–3 minutes.

### Step 8 — Verify the installation

```
corkscrew --help
```

You should see the help text. If you do, you are ready to go!

---

## Running Corkscrew for the first time

Before every session, make sure you:

1. Open your terminal (macOS: Terminal app; Windows: PowerShell).
2. Navigate to the Corkscrew folder:
   - macOS: `cd /path/to/eloi-wine`
   - Windows: `cd "C:\path\to\eloi-wine"`
3. Activate the virtual environment:
   - macOS: `source .venv/bin/activate`
   - Windows: `.venv\Scripts\Activate.ps1`

Then run your first download:

```
corkscrew run
```

This will download inventory files from all ~40 merchants and normalise them. Depending on your internet speed it may take 2–5 minutes.

---

## Command reference

### `corkscrew run`

**What it does:** Downloads wine inventory files from all (or selected) merchants and converts them to CSV.

**Basic usage:**

```
corkscrew run
```

This runs all enabled merchants across all tiers.

**Options:**

| Option | What it does | Example |
|--------|-------------|---------|
| `--merchant ID` | Download only one specific merchant | `corkscrew run --merchant farr-vintners` |
| `--tier N` | Download only merchants in tier N (1 = best coverage) | `corkscrew run --tier 1` |
| `--dry-run` | Shows what *would* be downloaded, without actually downloading anything | `corkscrew run --dry-run` |
| `--config PATH` | Use a different merchants config file | `corkscrew run --config my-merchants.yaml` |

**Examples:**

```bash
# Download everything
corkscrew run

# Preview what would be downloaded (no files saved)
corkscrew run --dry-run

# Download only Farr Vintners
corkscrew run --merchant farr-vintners

# Download all tier-1 merchants only
corkscrew run --tier 1
```

**What you will see on screen:**

```
Starting run for 36 merchants
  ✓ farr-vintners                          1234 KB  changed
  ✓ sterling-fine-wines                     892 KB  unchanged
    → 3421 wines normalized
  ✗ some-merchant                          Connection timeout
  ...

Run complete: 35/36 succeeded, 1 failed, 0 norm failures, 12843 wines normalized
```

- A green ✓ means the download succeeded.
- A red ✗ means it failed (the error reason is shown).
- "changed" means the file is new/updated since last time; "unchanged" means it's identical.
- "wines normalized" shows how many wine records were extracted.

**Exit codes** (useful for automation):
- `0` — all downloads and normalizations succeeded
- `1` — one or more downloads or normalizations failed
- `2` — the config file has an error (won't download anything)

---

### `corkscrew status`

**What it does:** Shows a summary table of every merchant — when it was last downloaded, whether it succeeded, and whether the data has changed recently.

**Usage:**

```
corkscrew status
```

**Example output:**

```
                      Corkscrew Status
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┓
┃ Merchant           ┃ Last Run ┃ Status   ┃ Changed ┃ Hash     ┃ Failures ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━┩
│ Farr Vintners      │ 2h ago   │ OK       │ Yes     │ a3f12b9c │ 0        │
│ Sterling Fine Wines│ 2h ago   │ STALE    │ No      │ 9dbc1234 │ 0        │
│ Some Merchant      │ 2h ago   │ FAILED   │ -       │ -        │ 2        │
└────────────────────┴──────────┴──────────┴─────────┴──────────┴──────────┘

36 merchants | 33 OK | 1 stale | 2 failed
```

**Status meanings:**

| Status | Meaning |
|--------|---------|
| `PENDING` | Never been downloaded yet |
| `OK` | Downloaded and normalised successfully |
| `STALE` | Downloaded successfully, but the file hasn't changed in many runs (merchant may have stopped updating) |
| `FAILED` | Last 1–2 downloads failed |
| `⚠ WARN` | Last 3–6 downloads failed — needs attention |
| `CRITICAL` | Last 7+ downloads failed — merchant URL may be broken |

The **Hash** column shows the first 8 characters of the file's unique fingerprint (SHA-256). If this changes between runs, the file's contents changed.

The **Failures** column shows how many consecutive failed downloads there have been.

---

### `corkscrew list`

**What it does:** Shows a simple table of all configured merchants, their tier, and whether they are enabled.

**Usage:**

```
corkscrew list
```

**Example output:**

```
                         Configured Merchants
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID                   ┃ Name                 ┃ Country ┃ Tier ┃ Enabled ┃ Pattern    ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ farr-vintners        │ Farr Vintners        │ UK      │ 1    │ ✓       │ static     │
│ sterling-fine-wines  │ Sterling Fine Wines  │ UK      │ 1    │ ✓       │ hub_wine   │
│ ...                  │ ...                  │ ...     │ ...  │ ...     │ ...        │
└──────────────────────┴──────────────────────┴─────────┴──────┴─────────┴────────────┘
```

The **Pattern** column describes how the download URL is constructed:
- `static` — a direct, unchanging URL
- `dated` — a URL that changes daily (e.g. includes today's date)
- `google_sheets` — a Google Sheets spreadsheet
- `google_drive` — a file on Google Drive
- `hub_wine` — uses the Hub Wine extranet
- `rest_endpoint` — a REST API endpoint
- `dynamic_php` — a dynamic PHP-generated file

---

### `corkscrew merge`

**What it does:** Combines the latest normalised CSV from every merchant into a single master file at `data/master/master.csv`.

**Usage:**

```
corkscrew merge
```

**Options:**

| Option | What it does | Example |
|--------|-------------|---------|
| `--output PATH` | Save the master file to a custom location | `corkscrew merge --output ~/Desktop/wines.csv` |

**Example output:**

```
✓ Merged 35 merchants → data/master/master.csv (12843 total records)
```

After running this, you can open `data/master/master.csv` in Excel or Google Sheets. Each row is one wine, and columns are standardised across all merchants.

---

## Understanding the output on screen

When you run `corkscrew run`, you will see messages like:

```
  ✓ farr-vintners                          1234 KB  changed
    → 3421 wines normalized
```

Here is what each part means:

- **✓** (green tick) — the download was successful
- **farr-vintners** — the merchant ID
- **1234 KB** — the size of the downloaded file in kilobytes
- **changed** — the file contents are different from last time (new data!)
- **unchanged** — the file is identical to last time (skips re-normalisation)
- **→ 3421 wines normalized** — how many wine records were extracted from this file

A failed download looks like:

```
  ✗ some-merchant                          Connection timeout
```

- **✗** (red cross) — the download failed
- **Connection timeout** — the reason it failed

---

## Where are my files?

All data is saved inside the `data/` folder within your Corkscrew directory:

```
data/
├── raw/                 ← The original files downloaded from merchants
│   ├── farr-vintners/
│   │   └── 2026-02-23/
│   │       └── farr-vintners.xlsx
│   └── ...
├── normalized/          ← The cleaned, standardised CSVs per merchant
│   ├── farr-vintners/
│   │   └── 2026-02-23.csv
│   └── ...
├── master/
│   └── master.csv       ← ⭐ This is the file you want to open in Excel
└── state.json           ← Internal log of run history (do not edit manually)
```

**The file you want most of the time is `data/master/master.csv`.**

To open it:
- **Windows:** Double-click it in File Explorer — it will open in Excel.
- **macOS:** Double-click it in Finder — it will open in Numbers or Excel.
- **Google Sheets:** Go to Google Sheets → File → Import → Upload → select the file.

The master CSV has these columns:

| Column | Description |
|--------|-------------|
| `merchant_id` | Which merchant this wine came from |
| `wine_name` | Name of the wine |
| `vintage` | Year (e.g. 2019) |
| `price` | Price (as a number, without currency symbol) |
| `currency` | Currency code (e.g. GBP, EUR, USD) |
| `quantity` | Number of bottles available |
| `format` | Bottle format (e.g. 75cl, Magnum) |
| `region` | Wine region (e.g. Bordeaux, Burgundy) |
| `appellation` | More specific location |
| `download_date` | When this data was downloaded |

---

## Troubleshooting

### "command not found: corkscrew"

You are either not in the right folder, or the virtual environment is not activated.

- **macOS:** Run `source .venv/bin/activate`
- **Windows:** Run `.venv\Scripts\Activate.ps1`

Then try `corkscrew --help` again.

---

### "No such file or directory: merchants.yaml"

You are not in the right folder. The command must be run from inside the `eloi-wine` directory.

- **macOS:** `cd /path/to/eloi-wine` (drag the folder into the terminal to get the path)
- **Windows:** `cd "C:\path\to\eloi-wine"`

---

### A merchant shows FAILED or CRITICAL in `corkscrew status`

This usually means the merchant's website changed their download URL or is temporarily unavailable. Options:
- Wait a day and run again — it may be a temporary outage.
- Check the merchant's website manually to see if they still offer a download link.

---

### "SSL certificate error" or "certificate verify failed"

On some older macOS installations, SSL certificates are not set up correctly.

Run this once:

```
/Applications/Python\ 3.xx/Install\ Certificates.command
```

(Replace `3.xx` with your Python version, e.g. `3.13`.)

---

### Everything is "unchanged" every run

This is expected if the merchants have not updated their inventory. Some merchants update daily, others weekly or monthly. The **STALE** status in `corkscrew status` will warn you if a merchant hasn't updated in more than 5 consecutive runs.

---

### "Permission denied" on Windows when activating the virtual environment

Run this once in PowerShell (you may need to open it as Administrator by right-clicking it):

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### The download is very slow

Some merchants have slow servers, and downloads are intentionally not rushed to be polite. With ~40 merchants and a 10-connection limit, a full run typically takes 2–5 minutes on a normal broadband connection.

---

## FAQ

**Q: How often should I run Corkscrew?**

A: Once a day is usually enough. Most merchants update their inventories overnight.

**Q: Can I run it automatically (e.g. every morning)?**

A: Yes. On macOS you can use `cron` or `launchd`. On Windows you can use Task Scheduler. Setting this up is beyond the scope of this README, but search for "schedule Python script macOS" or "schedule Python script Windows" for guides.

**Q: What if a merchant is missing from the list?**

A: The merchants are configured in `merchants.yaml`. You can open this file in any text editor to add new merchants. The format is documented in the comments inside the file.

**Q: The master CSV is huge — how do I find specific wines?**

A: Open it in Excel and use **Ctrl+F** (Windows) or **⌘+F** (macOS) to search, or use the column filters (click the dropdown arrows in the header row).

**Q: Do I need to re-install everything next time I use it?**

A: No. You only need to install once. Next time, just:
1. Open the terminal
2. Navigate to the eloi-wine folder
3. Activate the virtual environment (`source .venv/bin/activate` or `.venv\Scripts\Activate.ps1`)
4. Run `corkscrew run`
