import argparse
import sqlite3
import shlex
import sys
from datetime import date, timedelta
from tabulate import tabulate

connection = sqlite3.connect('C:/main/Code/expense-tracker/expences.db')
cursor = connection.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS expences (
id INTEGER PRIMARY KEY,
date TEXT NOT NULL,
category TEXT NOT NULL,
description TEXT NOT NULL,
amount_rub INTEGER NOT NULL
)
''')

cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
    ('tableformat', )
)
tableformat_exists = cursor.fetchone()

cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
    ('budget', )
)
budget_exists = cursor.fetchone()

if not tableformat_exists and not budget_exists:
    cursor.executescript('''
    CREATE TABLE tableformat (
    id INTEGER PRIMARY KEY,
    format INTEGER NOT NULL
    );
    INSERT INTO tableformat (format) VALUES (1)
    ''')

    cursor.executescript('''
    CREATE TABLE budget (
    id INTEGER PRIMARY KEY,
    budget INTEGER NOT NULL,
    status INTEGER NOT NULL
    );
    INSERT INTO budget (budget, status) VALUES (0, 0)
    ''')



parser = argparse.ArgumentParser(
    prog='exp-track',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=('''\
        This simple expense tracker has 5 main commands
        ------------------------------------------
         1. add --description {what money were spent on(1 word or sentence in ' '); optional} --amount {in rubles} --category {category of the expence(1 word); optional}
         (you can also add -y if expence was yesterday, -yy if it was 2 days ago and so on)
         2.1 delete --id {an id of an expence you want to delete}
         2.2 delete --month {a month of expences you want to delete}
         2.3 delete --category {a category of expences you want to delete}
         3.1 list --category {type the category you want to list; optional} --format {select a number up to 8, your choice will be saved; optioanl}
         3.2 list --month {type the month you want to list; optional} --format {select a number up to 8, your choice will be saved; optioanl}
         4.1 summary --month {a number of the month you want to summarise}
         4.2 summary --category {name of the category you want to summarise}
         5.1 budget --set {set the budget for current month, you will recieve a notification if you exceed it}
         5.2 budget --remain (if you want to see remaining budget)
         5.3 budget --active (to activate budget function)
         5.4 budget --unactive (to disable budget function)
         All commands besides '--active' and '--unactive' can be used in shortened form with one '-' and its first letter: '--description' --> '-d'
        '''))

parser.add_argument("command", help="initial command", type=str)
parser.add_argument("-d", "--description", type=str, help = "describe how you spent money using 'add'")
parser.add_argument("-a", "--amount", type = int, help = "type in the cost in rubles using 'add' ")
parser.add_argument("-i", "--id", type=int, help="type in id of an expence you want to delete using 'delete'")
parser.add_argument('-m', '--month',choices= [1,2,3,4,5,6,7,8,9,10,11,12], type=int, help="type in the number of the month you want to summarise or delete using 'summarise' or 'delete'")
parser.add_argument('-f', '--format', choices=[1,2,3,4,5,6,7, 8], type=int, help = "type in a number from 1 to 8 to select the table format using 'list'")
parser.add_argument('-c', '--category', type=str, help="type in a category of the expence using 'delete' 'list' 'summary'")
parser.add_argument('-y', '--yesterday', action='count', default=0, help = "type -y if you want to add yesterday's expence -yy if it was 2 days ago and so on  using 'add'")
parser.add_argument('-s', '--set', type=int, help = "type in a number to set the budget for current month in RUB using 'budget'")
parser.add_argument('-r', '--remain', action='store_true', help="use it to see the remaining budget for current month using 'budget'")
parser.add_argument('--active', action='store_true', help="activate budget function using 'budget'")
parser.add_argument('--unactive', action='store_true', help="disable budget function using 'budget'")

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


def run_command(args):
    match args.command:

        case "add": 
            if args.amount != None:
                cursor.execute('SELECT status FROM budget WHERE id = ?', ('1'))
                status = cursor.fetchall()[0][0]
                if status:
                    cursor.execute('SELECT budget FROM budget WHERE id = ?', ('1'))
                    new_budget = cursor.fetchall()[0][0] - args.amount
                    cursor.execute(f'UPDATE budget SET budget = {new_budget} WHERE id = {"1"}')
                

                if args.category == None:
                    category_value = 'empty'
                else: category_value = args.category

                if args.description == None:
                    description_value = 'empty'
                else: description_value = args.description

                cursor.execute('INSERT INTO expences (date, category, description, amount_rub) VALUES (?, ?, ?, ?)', 
                               (str(date.today() - timedelta(days=args.yesterday)), category_value, description_value, args.amount))
                cursor.execute('SELECT MAX(id) FROM expences')

                max_id = cursor.fetchone()[0]
                print(f'# expense added successfully (id: {max_id})')
                if status and new_budget <= 0: print(f'# you exceeded your budget, remaining budget is {new_budget} RUB')
            else:
                print("# the command should look like this: add --description {use letters to add description, optional} "
                "--amount {use only numbers to set the amount} --category {type the category of the expence, optional}")

        case "list":
            if args.category == None and args.month == None:
                cursor.execute('SELECT * FROM expences')
                all_ids = cursor.fetchall()
            elif args.category == None and args.month != None:
                str_month = str(args.month)
                if len(str_month) == 1:
                    str_month = '0' + str_month
                cursor.execute(f'SELECT * FROM expences WHERE date LIKE "____-{str_month}-__"')
                all_ids = cursor.fetchall()
            elif args.category != None and args.month == None:
                cursor.execute('SELECT * FROM expences WHERE category = ?', (args.category, ))
                all_ids = cursor.fetchall()
            else:
                str_month = str(args.month)
                if len(str_month) == 1:
                    str_month = '0' + str_month
                cursor.execute(f'SELECT * FROM expences WHERE category = ? AND date LIKE "____-{str_month}-__"', (args.category, ))
                all_ids = cursor.fetchall()
            list_result = [('id', 'date', 'category', 'description', 'amount(RUB)')]
            list_result.extend(all_ids)

            if args.format != None:
                cursor.execute('DELETE FROM tableformat WHERE id = ?', ('1'))
                cursor.execute(f'INSERT INTO tableformat (format) VALUES ({args.format})')

            cursor.execute('SELECT format FROM tableformat')

            final_format = (cursor.fetchall()[0][0])

            table_format = ['orgtbl', 'grid','simple_grid', 'double_grid', 'rounded_grid', 'simple_outline', 'outline', 'heavy_outline'][final_format - 1]


            print(tabulate(list_result, headers='firstrow', tablefmt=table_format))

        case "delete": 
            if args.month == None and args.category == None and args.id != None:
                cursor.execute('DELETE FROM expences WHERE id = ?', (str(args.id), ))
                print(f'# expence deleted successfully (id {args.id})')
            elif args.id == None and args.category == None and args.month != None:
                str_month = str(args.month)
                if len(str_month) == 1:
                    str_month = '0' + str_month
                cursor.execute(f'DELETE FROM expences WHERE date LIKE "____-{str_month}-__"')
                print(f'# expences in {months[args.month - 1]} deleted successfully')
            elif args.id == None and args.month == None and args.category != None:
                cursor.execute('DELETE FROM expences WHERE category = ?', (args.category, ))
                print(f'# expences deleted successfully (category {args.category})')
            else:
                print('# wrong syntax, the command should look like: \n 1. delete --id {an id number of an expence you want to delete}\n ' \
                '# 2. delete --month {a number of a month of expences you want to delte}\n ' \
                '# 3. delete --category {a category of expences you watn to delete}')

        case "summary": 
            if args.month != None and args.category == None:
                cursor.execute('SELECT date, amount_rub FROM expences')
                summary_results = cursor.fetchall()
                summary = 0
                results_flag = False
                for i in summary_results:
                    month = int(i[0].split('-')[1])
                    if month == args.month:
                        results_flag = True
                        summary += i[1]
                if results_flag:
                    print(f'# total expences for {months[args.month - 1]}: {summary} RUB')
                else:
                    print(f'# there were no expences in this month')
            elif args.month == None and args.category != None:
                cursor.execute('SELECT category, amount_rub FROM expences')
                summary_results = cursor.fetchall()
                summary = 0
                results_flag = False
                for i in summary_results:
                    category = i[0]
                    if category == args.category:
                        results_flag = True
                        summary += i[1]
                if results_flag:
                    print(f'# total expences for category {args.category}: {summary} RUB')
                else:
                    print(f'# there is no such category {args.category}')
            else:
                print('# wrong syntax, command should look like this: \n# 1. summary --month {a number of the month you want to summarise} \n# 2. summary --category {name of the category you want to summarise}' )

        case "budget":
            if args.remain and args.set == None:
                cursor.execute('SELECT * FROM budget')
                

                fetch_data = cursor.fetchall()[0]

                budget = fetch_data[1]
                status = 'active' if fetch_data[2] else 'unactive'
                if status == 'unactive':
                    print("# the budget fucntion is unactive, if you want to activate it type 'budget --active'")
                else:
                    print(f"# your reamining budget for current month is {budget} RUB")
                
            elif not(args.remain) and args.set != None and args.set >= 0:
                cursor.execute('DELETE FROM budget WHERE id = ?', ('1'))
                cursor.execute('INSERT INTO budget (budget, status) VALUES (?, ?)', (args.set, 1))
                print(f'# your budget for this month was set to {args.set} RUB, the budget function is active')
            elif args.active:
                cursor.execute(f"UPDATE budget SET status = {1} WHERE id = {'1'}")
                print('# budget fucntion is active now')
            elif args.unactive:
                cursor.execute(f"UPDATE budget SET status = {0} WHERE id = {'1'}")
                print('# budget fucntion is unactive now')
            else:
                print('# wrong syntax, the command should look like: \n 1. budget --set {set the budget(not less than 0) for current month, you will recieve a notification if you exceed it}\n 2. budget --reamin (if you want to see remaining budget)')


        case _: print("# Invalid input, use only: 'add' 'list' 'delete' 'summary' 'budget'")


if len(sys.argv) == 1:
    print("# interactive mode: type -h to see the help, type 'exit' to quit")
    while True:
        line = input('et> ').strip()
        if line == '':
            continue
        if line == 'exit':
            break
        try:
            args = parser.parse_args(shlex.split(line))
        except SystemExit:
            continue
        except ValueError:
            print('# wrong syntax, check the quotes')
            continue
        run_command(args)
        connection.commit()
else:
    args = parser.parse_args()
    run_command(args)


connection.commit()
connection.close()
