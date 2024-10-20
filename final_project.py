import pandas as pd

#Reading data
url1="https://raw.githubusercontent.com/vkovalai/Final_Project_/refs/heads/main/Electricity_20-09-2024.csv"
url2="https://raw.githubusercontent.com/vkovalai/Final_Project_/refs/heads/main/sahkon-hinta-010121-240924.csv"
dfA = pd.read_csv(url1, delimiter=";", decimal = ",")
dfB = pd.read_csv(url2)

# Change time format to datetime

dfA["Time"] = pd.to_datetime(dfA["Time"], format = " %d.%m.%Y %H:%M")
dfB["Time"] = pd.to_datetime(dfB["Time"], format="%d-%m-%Y %H:%M:%S")

#display(dfA.head())
#display(dfB.head())

#Join the two data frames according to time
df = pd.merge(dfA,dfB, on= "Time") #how= "left"

#Calculate the hourly bill paid (using information about the price and the consumption)
df = df[df["Time"].dt.year >= 2021].reset_index(inplace = False)
df = df.drop (columns= ["index"])
#display(df)

df["Hourly_bill_cents"] = df["Energy (kWh)"] * df["Price (cent/kWh)"]

#display(df)


#Visualization
import streamlit as st
import matplotlib.pyplot as plt

st.title("Electricity Consumption")
st.subheader("Data available from 01/2021 to 08/2024")

#Selector for time

Start_date= st.date_input("Start date", value=pd.to_datetime("2021-01-01"))
End_date= st.date_input("End date", value=pd.to_datetime("2024-08-31"))

filtered_df = df[(df["Time"] >= pd.to_datetime(Start_date)) & (df["Time"] <= pd.to_datetime(End_date))]

st.write(f"Showing range: {Start_date.strftime('%Y-%m-%d')} - {End_date.strftime('%Y-%m-%d')}")
total_consumption = filtered_df["Energy (kWh)"].sum()
st.write(f"Total consumption over the period: {round(total_consumption)} kWh")
total_bill = filtered_df ["Hourly_bill_cents"].sum()/100
st.write (f"Total bill over the period: {round (total_bill)} €")
avg_h_price = filtered_df["Price (cent/kWh)"].mean()
st.write (f"Average hourly price: {round (avg_h_price,2)} cents")
avg_paid_price = (total_bill/total_consumption)*100
st.write (f"Average paid price: {round(avg_paid_price,2)} cents")

#Selector for act over selected period

Grouping_Interval = st.selectbox ("Averaging period:", ["Daily", "Weekly", "Monthly"])

if Grouping_Interval == "Daily":
    freq = "D"
elif Grouping_Interval == "Weekly":
    freq ="W"
else:
    freq = "ME"

#Groubed values

grouped_df = filtered_df.resample(freq, on="Time").agg({
    "Energy (kWh)": "sum",
    "Price (cent/kWh)": "mean",
    "Hourly_bill_cents": "sum",
    "Temperature": "mean"
}).reset_index()
#Converting cents to euros
grouped_df["Hourly_bill_cents"] = grouped_df["Hourly_bill_cents"]*0.01


parameters = ["Energy (kWh)", "Price (cent/kWh)","Hourly_bill_cents", "Temperature"]
colors = ["b", "b","b","b"]
y_labels = ['Electricity Consumption (kWh)', 'Electricity Price (cent/kWh)','Electricity Bill (€)', 'Temperature']

for param, color, y_label in zip(parameters, colors, y_labels):
     fig, ax = plt.subplots(figsize=(17, 5))

     # Plot the data (with thicker lines)
     ax.plot(grouped_df["Time"], grouped_df[param], color=color, linewidth=3)

    # Generate ticks for quarters
     xticks = pd.date_range(start=grouped_df["Time"].min(), end=grouped_df["Time"].max(), freq='QS')

     # Create custom labels for the x-axis: Only display the year for January, and month names for others
     xtick_labels = [x.strftime('%Y') if x.month == 1 else x.strftime('%B') for x in xticks]

     # Set x-axis ticks and labels
     ax.set_xticks(xticks)
     ax.set_xticklabels(xtick_labels)

     # Set labels
     ax.set_xlabel('Time')
     ax.set_ylabel(y_label)
    
     # Horizontal grid lines
     ax.grid(True, axis='y', linestyle='-', color='gray', linewidth=0.7)
     ax.grid(False, axis='x')
     ax.set_xlim(grouped_df["Time"].min(), grouped_df["Time"].max())
     # Display the figure using Streamlit
     st.pyplot(fig)



