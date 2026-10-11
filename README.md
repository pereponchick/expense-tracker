# et: a command-line expense tracker

`et` is a small expense tracker you run from the terminal. It logs what you spend (in whole rubles), lets you filter and summarize it by category or month, and can warn you when you go over a monthly budget. Everything is stored locally in a SQLite file, with no account and no internet connection needed.

The project lives in the [`expense-tracker/`](expense-tracker) folder:

| Path | What it is |
|---|---|
| `expense-tracker/et.py` | The source code (Python) |
| `expense-tracker/dist/et.exe` | A ready-to-run Windows build, no Python required |
| `expense-tracker/build/`, `et.spec` | PyInstaller build files, only needed if you rebuild the exe |

## Quick start on Windows (no Python needed)

1. Download this repository (green **Code** button, then **Download ZIP**) or clone it.
2. Open a terminal (cmd, PowerShell or Git Bash) inside `expense-tracker/dist`.
3. Run a command:

```bash
et.exe add -a 250 -c food -d "lunch"
et.exe list
```

In PowerShell use `.\et.exe`, in Git Bash use `./et.exe`.

> **Run it from a terminal, not by double-clicking.** `et` takes a command (`add`, `list`, ...) each time you run it. If you double-click the exe, it has no command to run and the window closes immediately.
>
> Windows SmartScreen or your antivirus may warn about the exe, because it is an unsigned PyInstaller build. If you would rather not run it, use the Python version below.

## Run from source (any OS)

Requires **Python 3.10 or newer** (the code uses `match`) and the `tabulate` package:

```bash
pip install tabulate
python expense-tracker/et.py list
```

## Run it as `et` from anywhere

### Windows (using the exe)

1. Press `Win + R`, type `sysdm.cpl`, press Enter.
2. **Advanced**, then **Environment Variables**.
3. Select **Path** under your user variables, then **Edit**, **New**, and paste the full path to the `dist` folder, for example `C:\Users\you\expense-tracker\expense-tracker\dist`.
4. Click OK and **restart your terminal**.

Now `et list` works in any terminal window.

### macOS / Linux (using the Python script)

The exe is Windows-only, so add an alias to `~/.bashrc` or `~/.zshrc`:

```bash
alias et="python3 /full/path/to/expense-tracker/et.py"
```

Reload the shell (`source ~/.bashrc`) and use `et list`.

## Commands

Run `et -h` at any time to see the built-in help.

### Add an expense

```bash
et add -a 500 -c food -d "lunch"     # amount, category, description
et add -a 200                        # category and description are optional ("empty" if omitted)
et add -a 150 -c coffee -y           # -y = yesterday
et add -a 150 -c coffee -yy          # -yy = 2 days ago, -yyy = 3 days ago, and so on
```

Amounts are whole rubles (no kopecks).

### List expenses

```bash
et list                              # everything
et list -c food                      # one category
et list -m 9                         # one month (1-12)
et list -c food -m 9                 # both filters together
et list -f 3                         # choose a table style, 1-8
```

The table style you pick with `-f` is remembered for next time.

### Delete expenses

Give exactly one of these:

```bash
et delete -i 5                       # one expense, by id (see `et list`)
et delete -c food                    # every expense in a category
et delete -m 9                       # every expense in a month
```

Deleting cannot be undone.

### Summarize

```bash
et summary -m 9                      # total spent in a month
et summary -c food                   # total spent in a category
```

### Monthly budget

```bash
et budget -s 30000                   # set the budget and turn tracking on
et budget -r                         # show what is left
et budget --unactive                 # pause tracking
et budget --active                   # resume tracking
```

While tracking is on, every `add` subtracts its amount from the remaining budget. When the remainder reaches zero or goes below, `add` prints a warning.

## Good to know

- **The database goes in the folder you run `et` from.** The file `expences.db` (the spelling is intentional, and it is created automatically on first run) is created in your current directory. If you run `et` from two different folders you get two separate databases. Pick one folder and always run it from there, or you will wonder where your expenses went.
- **Months are not tied to a year.** `-m 9` means September of every year. `delete -m 9` removes September of all years.
- **The budget does not reset itself.** It is a single running number. Set it again with `budget -s` at the start of each month. Deleting an expense does not give the money back to the budget, and backdated expenses (`-y`) count against it too.
- **Back up `expences.db` if your data matters.** It is a plain SQLite file, so copying it is a backup.

## Rebuilding the exe

```bash
pip install pyinstaller tabulate
cd expense-tracker
pyinstaller --onefile et.py
```

The new exe appears in `dist/`.
