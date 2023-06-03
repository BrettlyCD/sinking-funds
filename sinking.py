import pandas as pd
import numpy as np
import datetime

from sinking_df import sinking_funds


#Define fuction for validating proper float user input
def valid_float(message):
    while True:
        try:
            count = float(input(message))
            if count >= 0:
                return count
                break
        except:
            print('You must input a numerical value.\n' + message)


#Parse df down to dictionary of upcoming payments
due_this_month = sinking_funds[sinking_funds['current_period_disburse'] < 0][['item','due_next','amount']]
due_dictionary = due_this_month.set_index('item').T.to_dict('list')


#Calculate aggregations from pandas df
expected_beginning_balance = sinking_funds['exp_current_balance'].sum()
current_period_savings = sinking_funds['monthly_sinking'].sum()
current_period_disbursements = sinking_funds['current_period_disburse'].sum()
net_period_activity = sinking_funds['current_month_activity'].sum()
target_ending_balance = sinking_funds['target_ending_balance'].sum()

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

user_interface()