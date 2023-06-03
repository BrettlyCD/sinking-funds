import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta


### DEFINE FUNCTION WITH ALL DF PROCESSES ###
def refresh_df():
    #Load expenses json to a pandas df
    exp = pd.json_normalize(pd.read_json('../data/exp.json')['expenses'])

    #Create a field that counts the number of months tracked for reporting purposes
    exp['tracked_months'] = (((datetime.datetime.today().year-exp.date_added.dt.year)*12) + ((datetime.datetime.today().month-exp.date_added.dt.month))).astype(int)

    #Create a last disbursed calculation based on excel file inputs, using while loop in df.iterrows()
    last_paid = [] #empty list for appending to

    for index, row in exp.iterrows():
        payment_date = row['first_due']
        if payment_date >= datetime.datetime.today():
            last_paid.append(np.nan) 
        else:
            while (((datetime.datetime.today().year-payment_date.dt.year)*12) + ((datetime.datetime.today().month-payment_date.dt.month))) > row['cadence']:
                payment_date += relativedelta(months=row['cadence'])
            last_paid.append(payment_date)

    exp['last_disbursed']  = last_paid #load created list into a new field

    #update dtype to datetime for future formula usage. Especially crucial if no past disbursements
    exp['last_disbursed'] = pd.to_datetime(exp['last_disbursed'], format='%m,%d,%Y')

    #Create a next due date field using the same method as above
    due_dates = []

    for index, row in exp.iterrows():
        next_date = row['first_due']
        while next_date < datetime.datetime.today():
            next_date += relativedelta(months=row['cadence'])
        due_dates.append(next_date)

    exp['due_next'] = due_dates

    #Create a months until due date field for potential future use
    exp['months_till_due'] = (((exp.due_next.dt.year-exp.date_added.dt.year)*12) + ((exp.due_next.dt.month-exp.date_added.dt.month))).astype(int)

    #Calculate how many months to save in total based on when we started. Adding the +1 to the second condition to include the starting month.
    exp['months_to_save'] = np.where(exp['tracked_months'] >= exp['cadence'], exp['cadence'], (((exp.due_next.dt.year-exp.date_added.dt.year)*12) + ((exp.due_next.dt.month-exp.date_added.dt.month))+1).astype(int))

    #Calculate how much to save for each category each month.
    exp['monthly_sinking'] = round(exp['amount'] / exp['months_to_save'],2)
    exp.replace([np.inf, -np.inf], np.nan, inplace=True) #adjust for any divide by 0 issues

    #Formula for how many months of saving you've already done on this cycle, which we'll use for estimated current balance
    exp['current_buildup'] = np.where(exp['last_disbursed'].isnull(), exp['tracked_months'], (((datetime.datetime.today().year-exp.last_disbursed.dt.year)*12) + ((datetime.datetime.today().month-exp.last_disbursed.dt.month))))
    #Convert to an integer
    exp['current_buildup'] = exp['current_buildup'].fillna(0).astype(int) #use fillna to make the conversion work with NaN values

    #Now we can calculate our estimated starting balance
    exp['exp_current_balance'] = exp['current_buildup'] * exp['monthly_sinking']

    #Calculate a disbursement, if there is any needed this month.
    exp['current_period_disburse'] = np.where((exp['due_next'].dt.month == datetime.datetime.today().month) & (exp['due_next'].dt.year == datetime.datetime.today().year), -exp['amount'], 0)

    #Calculate what the ending balance should be after transfers
    exp['target_ending_balance'] = exp['exp_current_balance'] + exp['monthly_sinking'] + exp['current_period_disburse']

    #Field for the inidivual item net activity
    exp['current_month_activity'] = exp['target_ending_balance'] - exp['exp_current_balance']

    #With this processed dataframe, I want to create a copy that we'll pull into another file for user interaction.
    sinking_funds = exp.copy()

    return sinking_funds