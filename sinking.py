import pandas as pd
import numpy as np
import datetime

from sinking_df import sinking_funds


#Define user input/validation fuctions
def valid_float(message):
    while True:
        try:
            count = float(input(message))
            if count >= 0:
                return count
                break
        except:
            print('You must input a numerical value.\n' + message)

def valid_select(message, n_choices):
    """Function for testing valid user input."""
    while True:
        try:
            answer = input(message).upper()
            if answer in input_options[:n_choices]:
                return answer
                break
            else:
                print(alert + ' Try again: ')
        except:
            print(alert + ' Try again: ')

def user_input_text(message):
    "Function for accepting user input of text and savings to a variable"
    var = str(input(message))
    return var

def valid_date(date_title):
    "Function for checking for valid date input"
    while True:
        try:
            year, month, day = map(int, input('Enter the ' + date_title + ' in YYYY-MM-DD format: ').split('-'))
            input_date = datetime.date(year, month, day)
            return input_date.strftime('%Y-%m-%d')
            break
        except:
            print('Please enter in YYYY-MM-DD format: ')
    
def get_items(json_path, json_var):
    "Take in json variables and return the list of titles to reference in other functions."
    #create list of items saved to data
    with open(json_path) as f:
        data = json.load(f)
        temp = data[json_var]
        item_list = [list(dict.values())[0] for dict in temp]
    return item_list

def exp_in_list(message, list, match_wanted):
    "Take a user input after a prompt and return TRUE/FALSE if it is in a given list or not"
    while True:
        var = str(input(message))
        if match_wanted == False:
            if var in list:
                print('This expense already exists, please choose another title: ')
            else:
                return var
                break
        else:
            if var in list:
                return var
                break
            else:
                print('Expense not in list, please enter a valid expense: ')

#define action functions
def add_exp(json_path, json_var):
    "Take user inputs, create a dictionary, and write that dictionary to a json file."

    #setup variables for input
    title = exp_in_list("Expense Title: ", get_items(json_path, json_var), False) #validate the input isn't already in the list
    cadence = valid_float("Monthly cadence (every x months): ")
    start_date = datetime.date.today().strftime('%Y-%m-%d')
    first_due = valid_date("Due Date")
    amount = valid_float("How much do you want to save?: ")
    
    #create dictionary from variables
    exp_dict = {"title": title, "cadence": cadence, "date_added": start_date, "first_due": first_due, "amount": amount}

    with open(json_path) as f:
        data = json.load(f)
        temp = data[json_var]
        temp.append(exp_dict)
        with open(json_path, 'w') as f:
            json.dump(data, f)

def update_exp(json_path, json_var):
    "Take user inputs and update the value of their choice."
    #user input validated against list of itmes
    item_to_update = exp_in_list("Which expense would you like to update?: \n",get_items(json_path, json_var), True)

    #user input on which field to update
    field_choice = valid_select("Which field would you like to update?:\nA) Title\nB) Cadence\nC) Date Added\nD) First Due\nE) Amount", 5)
    if field_choice == 'A':
        field = 'title'
    elif field_choice == 'B':
        field = 'cadence'
    elif field_choice == 'C':
        field = 'date_added'
    elif field_choice == 'D':
        field = 'first_due'
    elif field_choice == 'E':
        field = 'amount'

    #user input to update field, using an if statement to decice which input validation to use
    if field == ('title'):
        new_value = user_input_text("New Title: ")
    elif field in ('cadence', 'amount'):
        new_value = valid_float("New Value: ")
    else:
        new_value = valid_date("New Date: ")
    
    #write to JSON
    with open(json_path) as f:
        data = json.load(f)
        temp = data[json_var]
        index = next((index for (index, d) in enumerate(temp) if d['title'] == item_to_update), None)
        temp[index][field] = new_value
        with open('../data/exp.json', 'w') as f:
            json.dump(data, f)

def delete_expense(json_path, json_var):
    item_to_delete = exp_in_list("Which expense would you like to delete?: \n",get_items(json_path, json_var), True)
    
    with open(json_path, 'r') as f:
        data = json.load(f)
        temp = data[json_var]
        temp[:] = [d for d in temp if d.get('title') != item_to_delete]
        with open(json_path, 'w') as f:
            json.dump(data, f)

def view_expenses(df, index_col):
    print("Active Expenses: \n")
    print(df.set_index(index_col))


#Parse df down to dictionary of upcoming payments
due_this_month = sinking_funds[sinking_funds['current_period_disburse'] < 0][['item','due_next','amount']]
due_dictionary = due_this_month.set_index('item').T.to_dict('list')


#Calculate aggregations from pandas df
expected_beginning_balance = sinking_funds['exp_current_balance'].sum()
current_period_savings = sinking_funds['monthly_sinking'].sum()
current_period_disbursements = sinking_funds['current_period_disburse'].sum()
net_period_activity = sinking_funds['current_month_activity'].sum()
target_ending_balance = sinking_funds['target_ending_balance'].sum()


#define application
def user_interface():
    print("\n\nYou're expected current balance is: $" + str("{:.2f}".format(expected_beginning_balance)) + ".\n")

    actual_beg_balance = valid_float("What is your actual current balance?: \n")

    #calculate new features with that input
    actual_period_activity = target_ending_balance - actual_beg_balance
    balance_adj = expected_beginning_balance - actual_beg_balance

    #print user summary
    print("\n\n"+"-"*10 + "USER REPORT" + "-"*10)

    print("\nYou're expected current balance is: $" + str("{:.2f}".format(expected_beginning_balance)) + ".")
    print("You're actual current balance is: $" + str("{:.2f}".format(actual_beg_balance)) + ".\n")

    if actual_period_activity < 0:
        print("You should move $" + str("{:.2f}".format(-actual_period_activity)) + " from your sinking funds balance to your bill-paying account.")
    else:
        print("You should move $" + str("{:.2f}".format(actual_period_activity)) + " from your checking account to your sinking funds balance.")
    print("This is made up of: \n- $" + str("{:.2f}".format(current_period_savings)) + " savings for future expenses\n- $" + str("{:.2f}".format(-current_period_disbursements)) + " of disbursements for current month expenses\n- $"+ str("{:.2f}".format(balance_adj)) + " of balance adjustments\n")

    print("With these changes, your ending balance will be: $" + str("{:.2f}".format(target_ending_balance)) + ".\n")
    
    print("\nPAYMENTS DUE THIS MONTH:\n")
    for key, value in due_dictionary.items():
        print(key, 'is due on', value[0].strftime('%m-%d-%Y'), ': $', str("{:.2f}".format(value[1])))
    
    print("\n\n"+"-"*10 + "END REPORT" + "-"*10)

#run application
user_interface()