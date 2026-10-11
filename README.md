# et: a command-line expense tracker

`et` is a small expense tracker for the terminal. It logs what you spend (in whole rubles), lets you filter and summarize it by category or month, and can warn you when you go over a monthly budget. Everything is stored in a local SQLite file, with no account and no internet connection needed.

It has two modes: an **interactive mode** (double-click the exe and type commands at a prompt) and a **one-shot mode** (run a single command from a terminal).

The project lives in the [`expense-tracker/`](expense-tracker) folder:

| Path | What it is |
|---|---|
| `expense-tracker/dist/et.exe` | Ready-to-run Windows build, no Python required |
| `expense-tracker/et.py` | The source code (Python), runs on Windows, macOS and Linux |
| `expense-tracker/build/`, `et.spec` | PyInstaller build files, only needed if you rebuild the exe |

## Quick start: interactive mode (Windows)

1. Download this repository (green **Code** button, then **Download ZIP**) or clone it.
2. Double-click `expense-tracker/dist/et.exe`.
3. A console window opens with a prompt. Type commands **without** the `et` prefix:

```
et> add -a 250 -c food -d "lunch"
et> list
et> summary -c food
et> exit
```

Type `-h` for the built-in help and `exit` to quit. Every command is saved the moment it runs, so closing the window with the X is safe too.

The database file `expences.db` is created automatically **next to `et.exe`**, so keep the exe in a folder you can write to.

> Windows SmartScreen or your antivirus may warn about the exe, because it is an unsigned PyInstaller build. If you would rather not run it, use the Python version below.

## One-shot mode and the `et` command

You can also pass a command straight from a terminal (cmd, PowerShell or Git Bash). The program runs it and exits:

```bash
et.exe list
et.exe add -a 250 -c food
```

(In PowerShell use `.\et.exe`, in Git Bash `./et.exe`.)

To type just `et` from any folder, add the `dist` folder to your PATH:

1. Press `Win + R`, type `sysdm.cpl`, press Enter.
2. **Advanced**, then **Environment Variables**.
3. Select **Path** under your user variables, then **Edit**, **New**, and paste the full path to the `dist` folder, for example `C:\Users\you\expense-tracker\expense-tracker\dist`.
4. Click OK and **restart your terminal**.

Now `et list` runs one command, and plain `et` (no arguments) opens the interactive prompt. It does not matter which folder you run it from: you always get the same database, the one next to `et.exe`.

## Run from source (Windows, macOS, Linux)

Requires Python 3.10 or newer:

```bash
pip install tabulate
python expense-tracker/et.py            # interactive mode
python expense-tracker/et.py list       # one-shot mode
```

Here the database is created next to `et.py`.

On macOS or Linux, an alias gives you the short command. Add this to `~/.bashrc` or `~/.zshrc`:

```bash
alias et="python3 /full/path/to/expense-tracker/et.py"
```

## Commands

The examples below work as typed at the `et>` prompt. In one-shot mode, put `et` in front of them (`et list -c food`). Every option has a one-letter short form.

### Add an expense

```
add -a 500 -c food -d "lunch"     # amount, category, description
add -a 200                        # category and description are optional ("empty" if omitted)
add -a 150 -c coffee -y           # -y = yesterday
add -a 150 -c coffee -yy          # -yy = 2 days ago, -yyy = 3 days ago, and so on
```

Amounts are whole rubles (no kopecks). Keep the category to one word, and put a multi-word description in quotes.

### List expenses

```
list                              # everything
list -c food                      # one category
list -m 9                         # one month (1-12)
list -c food -m 9                 # both filters together
list -f 3                         # choose a table style, 1-8
```

The table style you pick with `-f` is remembered next time.

### Delete expenses

Give exactly one of these:

```
delete -i 5                       # one expense, by id (see `list`)
delete -c food                    # every expense in a category
delete -m 9                       # every expense in a month
```

Deleting cannot be undone.

### Summarize

```
summary -m 9                      # total spent in a month
summary -c food                   # total spent in a category
```

### Monthly budget

```
budget -s 30000                   # set the budget and turn tracking on
budget -r                         # show what is left
budget --unactive                 # pause tracking
budget --active                   # resume tracking
```

While tracking is on, every `add` subtracts its amount from the remaining budget. When the remainder reaches zero or goes below, `add` prints a warning.

## Good to know

- **Your data lives next to the program.** Moving or copying `et.exe` (or `et.py`) to another folder starts a fresh, empty database there. To take your data along, copy `expences.db` with it. It is a plain SQLite file, so copying it is also a backup.
- **Categories are case-sensitive.** `Food` and `food` are two different categories.
- **Months are not tied to a year.** `-m 9` means September of every year, so `delete -m 9` removes September of all years.
- **The budget does not reset itself.** It is a single running number, so set it again with `budget -s` at the start of each month. Deleting an expense does not give the money back to the budget, and backdated expenses (`-y`) count against it too.

## Rebuilding the exe

`et.exe` is a compiled snapshot of `et.py`. After you change the code, rebuild it for the change to show up in the exe:

```bash
pip install pyinstaller tabulate
cd expense-tracker
pyinstaller --onefile et.py
```

The new exe appears in `dist/`.
