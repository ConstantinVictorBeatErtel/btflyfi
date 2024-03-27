from openai import OpenAI
client = OpenAI()
import csv

# Collect input from the user
age = int(input("Enter your age: "))
monthly_income = float(input("Enter your monthly income ($): "))
monthly_expenses = float(input("Enter your monthly expenses ($): "))
risk_appetite = int(input("On a scale of 1 to 5, with 5 being the highest, what is your risk appetite? "))
goals = input("Are your goals short-term or long-term? Enter 'short' or 'long': ")
time_horizon_input = input("Is your time horizon short (<5 years), medium (5-10 years), or long (>10 years)? Enter 'short', 'medium', or 'long': ")

# Assign time horizon a numeric value
if time_horizon_input == 'short':
    time_horizon = 1
elif time_horizon_input == 'medium':
    time_horizon = 2
else:
    time_horizon = 3


# Dummy current cash balance question (not used in calculations below, but could be)
current_cash_balance = float(input("Enter your current cash balance ($): "))

# Simplified calculation based on provided input
saving_rate = (100 - (risk_appetite * 10 + time_horizon * 5 + (100 - ((age / 100) * 100)))) / 100
investment_amount = (monthly_income - monthly_expenses) * (1 - saving_rate)

# Define investment allocations (simplified and arbitrary for the purpose of this example)
investments = {
    'Savings': round((monthly_income - monthly_expenses) * saving_rate, 2),
    'Individual Stocks': round(investment_amount * 0.4, 2) if risk_appetite > 3 else 0,
    'ETFs': round(investment_amount * 0.3, 2),
    'Bonds': round(investment_amount * 0.2, 2),
    'Real Estate': round(investment_amount * 0.05, 2),
    'Gold': round(investment_amount * 0.025, 2),
    'Crypto': round(investment_amount * 0.025, 2) if risk_appetite == 5 else 0,
}

# Creating and writing to a CSV file
filename = "investment_plan.csv"
with open(filename, 'w', newline='') as csvfile:
    fieldnames = ['Investment Type', 'Monthly Allocation ($)']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for key, value in investments.items():
        writer.writerow({'Investment Type': key, 'Monthly Allocation ($)': value})

print(f"Investment plan saved to {filename}.")