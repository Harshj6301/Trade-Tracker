import streamlit as st
import pandas as pd
from datetime import datetime

# --- Core Data Structure ---
# Using a dictionary for simplicity and direct conversion to DataFrame
def get_default_trade_entry():
    return {
        "Trade Date": datetime.now().strftime("%Y-%m-%d"),
        "Stock/Symbol": "",
        "Strategy": "",
        "CE/PE": "CE",  # Added CE/PE
        "Entry Price": None,
        "Exit Price": None,
        "Lot Size": None,  # Changed to Lot Size
        "Quantity": None,  # Changed to Quantity
        "Total Quantity": None, # Added Total Quantity
        "Profit/Loss": None,
        "RRR": None,
        "Notes": "",
        "Image": None,
        "Level": None,
        "Criteria": None,
        "Current Wave": None, # Added Current Wave
    }

# --- Helper Functions ---

def calculate_profit_loss(entry_price, exit_price, total_quantity):
    """Calculates profit/loss, handling potential errors."""
    if entry_price is not None and exit_price is not None and total_quantity is not None:
        return (exit_price - entry_price) * total_quantity
    return None

def calculate_rrr(entry_price, exit_price, lot_size, quantity):
    """Calculates the Risk-Reward Ratio.
    Args:
        entry_price (float): The entry price of the trade.
        exit_price (float): The exit price of the trade.
        lot_size (float): The lot size of the trade.
        quantity (int): quantity of lots
    Returns:
        float: The Risk-Reward Ratio, or None if calculation is not possible.
    """
    if entry_price is not None and exit_price is not None and lot_size is not None and quantity is not None and lot_size != 0:
        position_size = lot_size * quantity
        return abs((exit_price - entry_price) / position_size)
    return None

def add_trade(trades, new_trade):
    """Adds a new trade to the list, and recalculates derived values.
       Handles missing data gracefully.
    """
    # Convert string inputs to numeric, handling empty strings
    try:
        new_trade["Entry Price"] = float(new_trade["Entry Price"]) if new_trade["Entry Price"] else None
        new_trade["Exit Price"] = float(new_trade["Exit Price"]) if new_trade["Exit Price"] else None
        new_trade["Lot Size"] = float(new_trade["Lot Size"]) if new_trade["Lot Size"] else None  # Changed
        new_trade["Quantity"] = int(new_trade["Quantity"]) if new_trade["Quantity"] else None  # Changed
    except ValueError:
        st.error("Invalid numeric input. Please enter numbers only for price and size.")
        return trades  # Return original trades to prevent adding invalid data

    # Calculate Total Quantity
    if new_trade["Lot Size"] is not None and new_trade["Quantity"] is not None:
        new_trade["Total Quantity"] = new_trade["Lot Size"] * new_trade["Quantity"]
    else:
        new_trade["Total Quantity"] = None

    # Calculate Profit/Loss and RRR.  These now handle None values correctly.
    new_trade["Profit/Loss"] = calculate_profit_loss(
        new_trade["Entry Price"], new_trade["Exit Price"], new_trade["Total Quantity"]
    )
    new_trade["RRR"] = calculate_rrr(
        new_trade["Entry Price"], new_trade["Exit Price"], new_trade["Lot Size"], new_trade["Quantity"]
    )

    trades.append(new_trade)
    return trades

def update_trade(trades, index, updated_trade):
    """Updates an existing trade in the list, recalculating derived values."""
    if 0 <= index < len(trades):
        try:
            updated_trade["Entry Price"] = float(updated_trade["Entry Price"]) if updated_trade["Entry Price"] else None
            updated_trade["Exit Price"] = float(updated_trade["Exit Price"]) if updated_trade["Exit Price"] else None
            updated_trade["Lot Size"] = float(updated_trade["Lot Size"]) if updated_trade["Lot Size"] else None #changed
            updated_trade["Quantity"] = int(updated_trade["Quantity"]) if updated_trade["Quantity"] else None #changed
        except ValueError:
            st.error("Invalid numeric input. Please enter numbers only for price and size.")
            return trades

       # Calculate Total Quantity
        if updated_trade["Lot Size"] is not None and updated_trade["Quantity"] is not None:
            updated_trade["Total Quantity"] = updated_trade["Lot Size"] * updated_trade["Quantity"]
        else:
            updated_trade["Total Quantity"] = None

        # Calculate Profit/Loss and RRR
        updated_trade["Profit/Loss"] = calculate_profit_loss(
            updated_trade["Entry Price"], updated_trade["Exit Price"], updated_trade["Total Quantity"]
        )
        updated_trade["RRR"] = calculate_rrr(
            updated_trade["Entry Price"], updated_trade["Exit Price"], updated_trade["Lot Size"], updated_trade["Quantity"]
        )
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

        # Format numeric columns for better readability.  Handle None values in the DataFrame.
        for col in ["Entry Price", "Exit Price", "Lot Size", "Profit/Loss", "RRR", "Quantity", "Total Quantity"]: #added "Total Quantity"
            if col in df.columns:  # Check if the column exists
                df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")

        # Display the DataFrame
        st.dataframe(df, hide_index=True)
    else:
        st.write("No trades recorded yet.")

def clear_all_trades():
    """Clears all trades."""
    st.session_state.trades = []

# --- Main App Function ---

def main():
    """Main function to run the Streamlit app."""
    st.title("Stock Trade Tracker")

    # Initialize session state for trades
    if "trades" not in st.session_state:
        st.session_state.trades = []
    if 'ce_pe' not in st.session_state:  # Initialize CE/PE state
        st.session_state.ce_pe = "CE"

    # --- Sidebar for Adding Trades ---
    st.sidebar.header("Add New Trade")
    new_trade = get_default_trade_entry()

    # Use columns to organize input fields
    col1, col2 = st.sidebar.columns(2)  # Adjust the number '2' as needed

    new_trade["Trade Date"] = col1.date_input("Trade Date", datetime.now())
    new_trade["Stock/Symbol"] = col1.text_input("Stock/Symbol").upper()
    new_trade["Strategy"] = col1.text_input("Strategy")
    # CE/PE Toggle Button
    if col1.button(st.session_state.ce_pe):
        st.session_state.ce_pe = "PE" if st.session_state.ce_pe == "CE" else "CE"
    new_trade["CE/PE"] = st.session_state.ce_pe  # Store the current state
    new_trade["Entry Price"] = col1.text_input("Entry Price", value="")
    new_trade["Exit Price"] = col1.text_input("Exit Price", value="")
    new_trade["Lot Size"] = col2.text_input("Lot Size", value="")  # Changed
    new_trade["Quantity"] = col2.text_input("Quantity", value="")  # Changed
    new_trade["Level"] = col2.number_input("Level", min_value=1, max_value=5, step=1, value=1)
    new_trade["Criteria"] = col2.text_input("Criteria")
    new_trade["Current Wave"] = col2.selectbox("Current Wave", options=[1, 2, 3, 4, 5, "A", "B", "C"]) # Added
    new_trade["Notes"] = st.sidebar.text_area("Notes", height=100)
    new_trade["Image"] = st.sidebar.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if st.sidebar.button("Add Trade"):
        st.session_state.trades = add_trade(st.session_state.trades, new_trade)
        st.success("Trade added!")

    # --- Main Area: Display and Edit Trades ---
    display_trades(st.session_state.trades)

    # Add an "Edit" button for each trade in the DataFrame
    if st.session_state.trades: # only show when there are trades
        st.header("Edit/Delete Trades")
        index_to_edit = st.number_input("Enter index of trade to edit/delete (starting from 0):",
                                        min_value=0, max_value=len(st.session_state.trades) - 1, step=1)

        col1, col2 = st.columns(2)
        if col1.button("Edit Trade"):
            if 0 <= index_to_edit < len(st.session_state.trades):
                edited_trade = get_default_trade_entry()
                trade_to_edit = st.session_state.trades[index_to_edit]

                # Populate the input fields with the existing trade data
                edited_trade["Trade Date"] = col1.date_input("Trade Date", pd.to_datetime(trade_to_edit["Trade Date"]))
                edited_trade["Stock/Symbol"] = col1.text_input("Stock/Symbol", value=trade_to_edit["Stock/Symbol"])
                edited_trade["Strategy"] = col1.text_input("Strategy", value=trade_to_edit["Strategy"])
                edited_trade["CE/PE"] = col1.text_input("CE/PE", value=trade_to_edit["CE/PE"]) # Added
                edited_trade["Entry Price"] = col1.text_input("Entry Price", value=trade_to_edit["Entry Price"])
                edited_trade["Exit Price"] = col1.text_input("Exit Price", value=trade_to_edit["Exit Price"])
                edited_trade["Lot Size"] = col2.text_input("Lot Size", value=trade_to_edit["Lot Size"])  # Changed
                edited_trade["Quantity"] = col2.text_input("Quantity", value=trade_to_edit["Quantity"])  # Changed
                edited_trade["Level"] = col2.number_input("Level", min_value=1, max_value=5, step=1, value=trade_to_edit["Level"])
                edited_trade["Criteria"] = col2.text_input("Criteria", value=trade_to_edit["Criteria"])
                edited_trade["Current Wave"] = col2.selectbox("Current Wave", options=[1, 2, 3, 4, 5, "A", "B", "C"], index = [1, 2, 3, 4, 5, "A", "B", "C"].index(trade_to_edit["Current Wave"]) ) # Added
                edited_trade["Notes"] = st.text_area("Notes", value=trade_to_edit["Notes"], height=100)
                edited_trade["Image"] = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"]) #keep same

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
        display_trades(st.session_state.trades)  # Update display after clearing

if __name__ == "__main__":
    main()
