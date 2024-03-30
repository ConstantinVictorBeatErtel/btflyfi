from openai import OpenAI
client = OpenAI()
import csv
import pandas as pd
import cvxpy as cp
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
import pandas as pd
file_path = '/Users/ConstiX/Downloads/all_returns_5.csv'
all_returns = pd.read_csv(file_path)

print("Hi and nice to meet you! Butterfly Financial is for informational purposes only and is designed to give you information on how you could preserve and build wealth. None of your data will be saved. At the end of this survey, you are provided with additional resources.")

def get_non_negative_float(prompt):
    """Ensures the input value is a non-negative float."""
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                raise ValueError
            return value
        except ValueError:
            print("Please enter a valid non-negative number.")

# Collect input from the user
age = get_non_negative_float("Enter your age: ")
monthly_income = get_non_negative_float("Enter your monthly income after tax($) and 401k: ")
monthly_expenses = get_non_negative_float("Enter your monthly expenses ($): ")
monthly_401k = get_non_negative_float("How much do you save for your 401k every month? ")
total_401k = get_non_negative_float("How much have you saved in your 401k? ")
risk_appetite = int(input("On a scale of 1 to 5, with 5 being the highest, what is your risk appetite? "))
etf_to_stock = int(input("On a scale of 1 to 5, with 5 being the highest, how comfortable are you to invest in individual stocks? "))

# Prompt the user for their stock investment preferences
user_stock_preference = input("What sort of stocks are you looking to invest in? ")

# Mapping time horizon input to a numeric value
time_horizons = {'short': 1, 'medium': 2, 'long': 3}
time_horizon_input = input("Is your time horizon short (<5 years), medium (5-10 years), or long (>10 years)? Enter 'short', 'medium', or 'long': ")
time_horizon = time_horizons.get(time_horizon_input, 1)

other_projects = get_non_negative_float("Are you saving for any projects? If yes, please tell us how much you need to save. Otherwise please reply with '0':")
other_projects_time = get_non_negative_float("If you are saving for a project, please enter the number of months by when you would like to purchase it. Otherwise please reply with '0':")

current_cash_balance = get_non_negative_float("Enter your current combined cash, savings and investment balance excluding 401K($): ")

if age < 30:
    required_401k = 0.5 * (monthly_income * 12)

elif age >= 30 and age <40:
    required_401k = 1 * (monthly_income * 12)

elif age >= 40 and age <50:
    required_401k = 3 * (monthly_income * 12)

elif age >= 50 and age <65:
    required_401k = 6 * (monthly_income * 12)

else: 
    required_401k = 10 * (monthly_income * 12)

if required_401k > (total_401k + 36 * monthly_401k):
    additional_401k_monthly = (required_401k - (total_401k + 36 * monthly_401k))/36 
    monthly_income = monthly_income - additional_401k_monthly

else: 
    additional_401k_monthly = 0


if age > 50:
    required_savings = monthly_expenses * 6

elif age > 40 and age < 50: 
    required_savings = monthly_expenses * 5

elif age > 30 and age < 40: 
    required_savings = monthly_expenses * 4

else: 
    required_savings = monthly_expenses * 3


if current_cash_balance >= required_savings:
    required_monthly_savings = 0

elif current_cash_balance < required_savings and risk_appetite > 3:
    required_monthly_savings = (required_savings - current_cash_balance)/24

elif current_cash_balance < required_savings and risk_appetite < 3:
    required_monthly_savings = (required_savings - current_cash_balance)/12

elif current_cash_balance < required_savings and risk_appetite == 3:
    required_monthly_savings = (required_savings - current_cash_balance)/18

remaining_project = 0

if current_cash_balance >= (required_savings + other_projects):
    required_monthly_project_savings = 0
    current_other_project_savings = other_projects

elif current_cash_balance >= required_savings and (current_cash_balance - required_savings) < other_projects:
    remaining_project = (other_projects - (current_cash_balance - required_savings))
    required_monthly_project_savings = remaining_project/other_projects_time
    current_other_project_savings = current_cash_balance - required_savings

elif current_cash_balance < required_savings:
    required_monthly_project_savings = other_projects/other_projects_time
    current_other_project_savings = 0

# Old Code
saving_rate = max(0, (100 - (risk_appetite * 10 + time_horizon * 5 + (100 - (age / 100) * 100))) / 100)
#monthly_investment_amount = (monthly_income - monthly_expenses) * (1 - saving_rate)

# Determine the initial investment amount from current cash balance
initial_investment_amount = current_cash_balance

#Adjust risk appetite based on age:
if age < 30 and risk_appetite != 5:
    risk_appetite = risk_appetite + 1
if age > 50 and risk_appetite != 1:
    risk_appetite = risk_appetite - 1
else: 
    None


# Determine the minimum expected return based on user inputs (simplified example)
if risk_appetite == 1:
    min_expected_return = 0.005
elif risk_appetite == 2:
    min_expected_return = 0.007
elif risk_appetite  == 3:
    min_expected_return = 0.009
elif risk_appetite  == 4:
    min_expected_return = 0.01
else:  # High risk appetite
    min_expected_return = 0.011

expected_returns = all_returns.mean()

# Number of assets
n_assets = 5

# Portfolio weights variable
w = cp.Variable(n_assets)
cov_matrix = all_returns.cov()

# Objective: Minimize portfolio risk (standard deviation)
objective = cp.Minimize(cp.quad_form(w, cov_matrix))

# Constraints
constraints = [
    cp.sum(w) == 1,  # Sum of weights must be 1
    w >= 0,  # No short selling
    cp.matmul(w, expected_returns) >= min_expected_return,  # Corrected expected return constraint
]

# Problem
prob = cp.Problem(objective, constraints)

# Solve the problem
prob.solve()

# Output the optimal weights
optimal_weights = w.value

etf_to_stock_percentage = 0

if etf_to_stock == 5: 
    etf_to_stock_percentage = 0.7
elif etf_to_stock == 4: 
    etf_to_stock_percentage = 0.5
elif etf_to_stock == 3: 
    etf_to_stock_percentage = 0.3
elif etf_to_stock == 2: 
    etf_to_stock_percentage = 0.1
elif etf_to_stock == 1: 
    etf_to_stock_percentage = 0



# Determine the monthly investment amount from monthly income
extra_income = (monthly_income - monthly_expenses - required_monthly_savings - required_monthly_project_savings) 

current_allocations = {
    "Current 401K": round(total_401k,2),
    "Monthly 401K": 0,
    'Emergency Savings': round(min(current_cash_balance, required_savings), 2),
    'Project Savings': round(current_other_project_savings, 2),
    'Extra Savings': 0,
    'Individual Stocks': 0,
    'ETFs': 0,
    'Bonds': 0,
    'Real Estate': 0,
    'Gold': 0,
    'Crypto': 0,
}

crypto_income = 0
crypto_cash = 0

extra_cash = current_cash_balance - required_savings - other_projects

if risk_appetite == 5: 
    crypto_income = 0.05 * extra_income
    crypto_cash = 0.05 * extra_cash
    extra_income = extra_income * 0.95
    extra_cash = extra_cash * 0.95    
else: 
    None

# Send the user's preference to the model and ask for recommendations
completion = client.chat.completions.create(
  model="gpt-4-turbo-preview",
  messages=[
    {"role": "system", "content": "You are a financial assistant, providing tailored stock investment recommendations."},
    {"role": "user", "content": f"I am looking to invest in stocks related to {user_stock_preference}. That into consideration that I have risk appetite of {risk_appetite} on a scale of 1-5 with 5 being the highest. Can you recommend some options? Can you please make this recommendation a table with the first column being the company, the second column being the suggest allocation, and the third one being the explanation?"}
  ]
)

# Check if there are any choices and messages in the response
if completion.choices and completion.choices[0].message:
    # Directly accessing the text content within the chosen completion message
    completion_text = completion.choices[0].message.content
else:
    completion_text = "No completion found."

# Now, with completion_text correctly holding the string content, proceed to split and process it.
lines = completion_text.strip().split('\n')

extracted_data = []

if lines:
    # Assuming the completion text contains a table and starts with headers from the third line onwards
    data_lines = lines[2:]  # Adjust index if necessary based on your completion structure

    for line in data_lines:
        # Ensure it’s a valid table row
        if "|" in line:
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            # Make sure the row is formatted as expected with 3 columns: Company, Suggested Allocation, Explanation
            if len(cells) == 3:
                extracted_data.append((cells[0], cells[1], cells[2]))  # Tuple: (Company, Suggested Allocation, Explanation)

monthly_allocations = {
    "Monthly 401K": round(monthly_401k + additional_401k_monthly, 2),
    'Emergency Savings': round(required_monthly_savings, 2),
    'Project Savings': round(required_monthly_project_savings, 2),
    'Extra Savings': round(extra_income * optimal_weights[0], 2),
    'Individual Stocks': round(extra_income * optimal_weights[2] * etf_to_stock_percentage, 2),
    'ETFs': round(extra_income * optimal_weights[2] * (1-etf_to_stock_percentage), 2),
    'Bonds': round(extra_income * optimal_weights[1], 2),
    'Real Estate': round(extra_income * optimal_weights[3], 2),
    'Gold': round(extra_income * optimal_weights[4], 2),
    'Crypto': round(crypto_income, 2) if risk_appetite == 5 else 0,
}

if current_cash_balance > (required_savings + other_projects):
    # Assuming extra cash is allocated similarly to extra income investments
    current_allocations['Extra Savings'] += round(extra_cash * optimal_weights[0], 2) 
    current_allocations['Individual Stocks'] += round(extra_cash * optimal_weights[2] * etf_to_stock_percentage, 2) 
    current_allocations['ETFs'] += round(extra_cash * optimal_weights[2] * (1-etf_to_stock_percentage), 2)
    current_allocations['Bonds'] += round(extra_cash * optimal_weights[1], 2)
    current_allocations['Real Estate'] += round(extra_cash * optimal_weights[3], 2)
    current_allocations['Gold'] += round(extra_cash * optimal_weights[4], 2)
    if risk_appetite == 5:
        current_allocations['Crypto'] += round(crypto_cash, 2)

# Creating and writing to a CSV file
filename = "investment_plan.csv"
with open(filename, mode='w', newline='') as csvfile:
    fieldnames = ['Investment Type', 'Investment of Initial Capital ($)', 'Allocation of Monthly Income($)']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for key in current_allocations:
        writer.writerow({
            'Investment Type': key,
            'Investment of Initial Capital ($)': current_allocations[key],
            'Allocation of Monthly Income($)': monthly_allocations.get(key, '-') # Use '-' if no monthly allocation for that investment type
        })

# Define the filename for the example portfolio
portfolio_filename = "example_portfolio.csv"

# Create and write to the new CSV file
with open(portfolio_filename, mode='w', newline='', encoding='utf-8') as portfolio_file:
    # Define the fieldnames (column headers) for the portfolio
    fieldnames = ['Company', 'Suggested Allocation', 'Explanation']
    
    # Initialize the CSV writer with the defined fieldnames
    writer = csv.DictWriter(portfolio_file, fieldnames=fieldnames)
    
    # Write the header row
    writer.writeheader()
    
    # Iterate through the extracted_data to write each stock's information
    for stock_info in extracted_data:
        company, allocation, explanation = stock_info
        
        # Write the row for the current stock
        writer.writerow({
            'Company': company,
            'Suggested Allocation': allocation,
            'Explanation': explanation
        })

completion_2 = client.chat.completions.create(
  model="gpt-4-turbo-preview",
  messages=[
    {"role": "system", "content": "You are a financial assistant, providing general information about how to build wealth"},
    {"role": "user", "content": f"Can you please provide me with 1-2 general tips to build wealth as well as resources to educate myself further?"}
  ]
)

# Print the model's recommendations based on the response
print(completion_2.choices[0].message)
print(extracted_data)
print(f"Investment plan saved to {filename}.")
print(f"Exmaple portfolio plan saved to {portfolio_filename}.")