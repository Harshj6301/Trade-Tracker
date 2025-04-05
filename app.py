import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Set default page config to wide mode
st.set_page_config(layout="wide")

# --- Core Data Structure ---
# Using a dictionary for simplicity and direct conversion to DataFrame
def get_default_trade_entry():
    return {
        "Date": datetime.now().strftime("%Y-%m-%d"), # Changed to Date
        "Stock/Symbol": "",
        "Strategy": "",
        "CE/PE": "CE",
        "Strike Price": None, # Added Strike Price
        "Expiry Date": None, # Added Expiry Date
        "LTP": None,
        "Lot Size": None,
        "Quantity": None,
        "Total Quantity": None,
        "Buy Size": None, # Added Buy Size
        "Notes": "",
        "Image": None,
        "C Level": None,
        "Criteria": [],
        "Current Wave": None,
    }

# --- Helper Functions ---

def calculate_buy_size(total_quantity, ltp):
    """Calculates the Buy Size.
    Args:
        total_quantity (int): The total quantity.
        ltp (float): The LTP.
    Returns:
        float: The Buy Size
    """
    if total_quantity is not None and ltp is not None:
        return total_quantity * ltp
    return None

def add_trade(trades, new_trade):
    """Adds a new trade to the list, and calculates derived values.
    """
    # Convert string inputs to numeric, handling empty strings
    try:
        new_trade["LTP"] = float(new_trade["LTP"]) if new_trade["LTP"] else None
        new_trade["Lot Size"] = float(new_trade["Lot Size"]) if new_trade["Lot Size"] else None
        new_trade["Quantity"] = int(new_trade["Quantity"]) if new_trade["Quantity"] else None
        new_trade["Strike Price"] = float(new_trade["Strike Price"]) if new_trade["Strike Price"] else None # Added
    except ValueError:
        st.error("Invalid numeric input. Please enter numbers only for LTP, lot size, quantity and strike price.")
        return trades

    # Calculate Total Quantity
    if new_trade["Lot Size"] is not None and new_trade["Quantity"] is not None:
        new_trade["Total Quantity"] = new_trade["Lot Size"] * new_trade["Quantity"]
    else:
        new_trade["Total Quantity"] = None

     # Calculate Buy Size
    new_trade["Buy Size"] = calculate_buy_size(new_trade["Total Quantity"], new_trade["LTP"])

    trades.append(new_trade)
    return trades

def update_trade(trades, index, updated_trade):
    """Updates an existing trade in the list, recalculating derived values."""
    if 0 <= index < len(trades):
        try:
            updated_trade["LTP"] = float(updated_trade["LTP"]) if updated_trade["LTP"] else None
            updated_trade["Lot Size"] = float(updated_trade["Lot Size"]) if updated_trade["Lot Size"] else None
            updated_trade["Quantity"] = int(updated_trade["Quantity"]) if updated_trade["Quantity"] else None
            updated_trade["Strike Price"] = float(updated_trade["Strike Price"]) if updated_trade["Strike Price"] else None # Added

        except ValueError:
            st.error("Invalid numeric input. Please enter numbers only for LTP, lot size, quantity and strike price.")
            return trades

        # Calculate Total Quantity
        if updated_trade["Lot Size"] is not None and updated_trade["Quantity"] is not None:
            updated_trade["Total Quantity"] = updated_trade["Lot Size"] * updated_trade["Quantity"]
        else:
            updated_trade["Total Quantity"] = None

        # Calculate Buy Size
        updated_trade["Buy Size"] = calculate_buy_size(updated_trade["Total Quantity"], updated_trade["LTP"])
        trades[index] = updated_trade
    return trades

def delete_trade(trades, index):
    """Deletes a trade from the list."""
    if 0 <= index < len(trades):
        del trades[index]
    return trades

def display_trades(trades):
    """Displays the trades in a Streamlit DataFrame, with formatting."""
    if trades:
        df = pd.DataFrame(trades)
        df['Expiry Display'] = df.apply(lambda row: f"{pd.to_datetime(row['Expiry Date']).strftime('%d %b')} {int(row['Strike Price'])} {row['CE/PE']}"
                                          if pd.notnull(row['Expiry Date']) and pd.notnull(row['Strike Price'])
                                          else 'N/A', axis=1)
        # Format numeric columns for better readability.
        for col in ["LTP", "Lot Size", "Quantity", "Total Quantity", "C Level","Buy Size"]: # Removed RRR
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")

        # Display the DataFrame
        st.dataframe(df[['Date', 'Stock/Symbol', 'Strategy', 'CE/PE',  'Expiry Display', 'LTP', 'Lot Size', 'Quantity', 'Total Quantity', 'Buy Size', 'Notes', 'Image', 'C Level', 'Criteria', 'Current Wave']], hide_index=True) # Removed RRR and added Expiry Display
    else:
        st.write("No trades recorded yet.")



def clear_all_trades():
    """Clears all trades."""
    st.session_state.trades = []

def export_to_csv(trades):
    """Exports the trades data to a CSV file."""
    if trades:
        df = pd.DataFrame(trades)
        # Use a string buffer to hold the CSV data in memory
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)  #  index=False to avoid writing the DataFrame index
        csv_content = csv_buffer.getvalue()  # Get the string value from the buffer
        return csv_content
    else:
        return None

def import_from_csv(file):
    """Imports trades data from a CSV file."""
    try:
        df = pd.read_csv(file)
        # Convert 'Trade Date' to datetime objects, handling potential parsing issues
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce') # Changed to Date
        # Drop rows where 'Trade Date' is NaT (Not a Time) after conversion
        df.dropna(subset=['Date'], inplace=True)

        # Convert the DataFrame to a list of dictionaries, which is the format used
        trades = df.to_dict(orient='records')
        return trades
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return None

# --- Main App Function ---
def main():
    """Main function to run the Streamlit app."""
    st.title("Watchlist Tracker")

    # Initialize session state
    if "trades" not in st.session_state:
        st.session_state.trades = []
    if 'ce_pe' not in st.session_state:
        st.session_state.ce_pe = "CE"

    # --- Sidebar for Adding Trades ---
    st.sidebar.header("Add New Trade")
    new_trade = get_default_trade_entry()

    # Use columns to organize input fields
    col1, col2 = st.sidebar.columns(2)

    new_trade["Date"] = col1.date_input("Date", datetime.now()) # Changed to Date
    new_trade["Stock/Symbol"] = col1.text_input("Stock/Symbol").upper()
    strategy_options = ['GZ-GZ', 'DZ-DZ', '3rd wave', '5th wave', 'C wave']
    new_trade["Strategy"] = col1.selectbox("Strategy", options=strategy_options)
    new_trade["CE/PE"] = col1.radio("CE/PE", options=["CE", "PE"], index=0)
    new_trade["Strike Price"] = col1.number_input("Strike Price", step=50, value=0) # Added Strike Price
    new_trade["Expiry Date"] = col1.date_input("Expiry Date") # Added Expiry Date
    new_trade["LTP"] = col1.text_input("LTP", value="")
    new_trade["Lot Size"] = col2.number_input("Lot Size", value=0)
    new_trade["Quantity"] = col2.number_input("Quantity", value=1, step=1)
    new_trade["C Level"] = col2.number_input("C Level", min_value=1, max_value=5, step=1, value=1)
    criteria_options = ['MBL break-retest', 'Auto break-retest', 'RBD', 'HBD', 'BAP']
    new_trade["Criteria"] = col2.multiselect("Criteria", options=criteria_options)
    new_trade["Current Wave"] = col2.selectbox("Current Wave", options=[1, 2, 3, 4, 5, "A", "B", "C"])
    new_trade["Notes"] = st.sidebar.text_area("Notes", height=100)
    new_trade["Image"] = st.sidebar.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if st.sidebar.button("Add Trade"):
        st.session_state.trades = add_trade(st.session_state.trades, new_trade)
        st.success("Trade added!")

    # --- Main Area: Display and Edit Trades ---
    display_trades(st.session_state.trades)

    # Add an "Edit" button for each trade in the DataFrame
    if st.session_state.trades:
        st.header("Edit/Delete Trades")
        index_to_edit = st.number_input("Enter index of trade to edit/delete (starting from 0):",
                                        min_value=0, max_value=len(st.session_state.trades) - 1, step=1)

        col1, col2 = st.columns(2)
        if col1.button("Edit Trade"):
            if 0 <= index_to_edit < len(st.session_state.trades):
                edited_trade = get_default_trade_entry()
                trade_to_edit = st.session_state.trades[index_to_edit]

                # Populate the input fields with the existing trade data
                edited_trade["Date"] = col1.date_input("Date", pd.to_datetime(trade_to_edit["Date"])) # Changed to Date
                edited_trade["Stock/Symbol"] = col1.text_input("Stock/Symbol", value=trade_to_edit["Stock/Symbol"])
                edited_trade["Strategy"] = col1.selectbox("Strategy", options=strategy_options, index=strategy_options.index(trade_to_edit["Strategy"]))
                edited_trade["CE/PE"] = col1.radio("CE/PE", options=["CE", "PE"], index= ["CE", "PE"].index(trade_to_edit["CE/PE"]))
                edited_trade["Strike Price"] = col1.number_input("Strike Price", step=50, value=edited_trade["Strike Price"]) # Added
                edited_trade["Expiry Date"] = col1.date_input("Expiry Date", value = pd.to_datetime(trade_to_edit["Expiry Date"])) # Added
                edited_trade["LTP"] = col1.text_input("LTP", value=trade_to_edit["LTP"])
                edited_trade["Lot Size"] = col2.number_input("Lot Size", value=trade_to_size["Lot Size"])
                edited_trade["Quantity"] = col2.number_input("Quantity", value=trade_to_edit["Quantity"], step=1)
                edited_trade["C Level"] = col2.number_input("C Level", min_value=1, max_value=5, step=1, value=trade_to_edit["C Level"])
                edited_trade["Criteria"] = col2.multiselect("Criteria", options=criteria_options, default=trade_to_edit["Criteria"])
                edited_trade["Current Wave"] = col2.selectbox("Current Wave", options=[1, 2, 3, 4, 5, "A", "B", "C"], index = [1, 2, 3, 4, 5, "A", "B", "C"].index(trade_to_edit["Current Wave"]))
                edited_trade["Notes"] = st.text_area("Notes", value=trade_to_edit["Notes"], height=100)
                edited_trade["Image"] = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

                st.session_state.trades = update_trade(st.session_state.trades, index_to_edit, edited_trade)
                st.success("Trade updated!")
            else:
                st.error("Invalid index. Please enter a valid index to edit.")

        if col2.button("Delete Trade"):
            st.session_state.trades = delete_trade(st.session_state.trades, index_to_edit)
            st.success("Trade deleted!")

    # Add a button to clear all trades
    if st.button("Clear All Trades"):
        clear_all_trades()
        st.warning("All trades cleared!")
        display_trades(st.session_state.trades)

    # Add buttons for exporting and importing data
    col1, col2 = st.columns(2)
    csv_data = export_to_csv(st.session_state.trades)
    if csv_data:
        col1.download_button(
            label="Export to CSV",
            data=csv_data,
            file_name="trades.csv",
            mime="text/csv",
        )

    uploaded_file = col2.file_uploader("Import from CSV", type="csv")
    if uploaded_file is not None:
        imported_trades = import_from_csv(uploaded_file)
        if imported_trades:
            st.session_state.trades = imported_trades
            st.success("Data imported successfully!")
            display_trades(st.session_state.trades)
        else:
            st.error("Failed to import data from CSV.")

if __name__ == "__main__":
    main()
