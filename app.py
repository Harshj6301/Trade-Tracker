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
        "CE/PE": "CE",
        "Entry Price": None,
        "Exit Price": None,
        "Lot Size": None,
        "Quantity": None,
        "Total Quantity": None,
        "Profit/Loss": None,
        "RRR": None,
        "Notes": "",
        "Image": None,
        "Confidence Level": None,  # Changed
        "Criteria": [],  # Changed to list for multiselect
        "Current Wave": None,
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
    """
    # Convert string inputs to numeric, handling empty strings
    try:
        new_trade["Entry Price"] = float(new_trade["Entry Price"]) if new_trade["Entry Price"] else None
        new_trade["Exit Price"] = float(new_trade["Exit Price"]) if new_trade["Exit Price"] else None
        new_trade["Lot Size"] = float(new_trade["Lot Size"]) if new_trade["Lot Size"] else None
        new_trade["Quantity"] = int(new_trade["Quantity"]) if new_trade["Quantity"] else None
    except ValueError:
        st.error("Invalid numeric input. Please enter numbers only for price, lot size and quantity.")
        return trades

    # Calculate Total Quantity
    if new_trade["Lot Size"] is not None and new_trade["Quantity"] is not None:
        new_trade["Total Quantity"] = new_trade["Lot Size"] * new_trade["Quantity"]
    else:
        new_trade["Total Quantity"] = None

    # Calculate Profit/Loss and RRR.
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
            updated_trade["Lot Size"] = float(updated_trade["Lot Size"]) if updated_trade["Lot Size"] else None
            updated_trade["Quantity"] = int(updated_trade["Quantity"]) if updated_trade["Quantity"] else None
        except ValueError:
            st.error("Invalid numeric input. Please enter numbers only for price, lot size and quantity.")
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

        # Format numeric columns for better readability.
        for col in ["Entry Price", "Exit Price", "Lot Size", "Profit/Loss", "RRR", "Quantity", "Total Quantity"]:
            if col in df.columns:
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

    new_trade["Trade Date"] = col1.date_input("Trade Date", datetime.now())
    new_trade["Stock/Symbol"] = col1.text_input("Stock/Symbol").upper()
    strategy_options = ['GZ-GZ', 'DZ-DZ', '3rd wave', '5th wave', 'C wave']
    new_trade["Strategy"] = col1.selectbox("Strategy", options=strategy_options)
    new_trade["CE/PE"] = col1.radio("CE/PE", options=["CE", "PE"], index=0)
    new_trade["Entry Price"] = col1.text_input("Entry Price", value="")
    new_trade["Exit Price"] = col1.text_input("Exit Price", value="")
    new_trade["Lot Size"] = col2.number_input("Lot Size", value=0)
    new_trade["Quantity"] = col2.number_input("Quantity", value=1, step=1)
    new_trade["Confidence Level"] = col2.number_input("Confidence Level", min_value=1, max_value=5, step=1, value=1)
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
                edited_trade["Trade Date"] = col1.date_input("Trade Date", pd.to_datetime(trade_to_edit["Trade Date"]))
                edited_trade["Stock/Symbol"] = col1.text_input("Stock/Symbol", value=trade_to_edit["Stock/Symbol"])
                edited_trade["Strategy"] = col1.selectbox("Strategy", options=strategy_options, index=strategy_options.index(trade_to_edit["Strategy"]))
                edited_trade["CE/PE"] = col1.radio("CE/PE", options=["CE", "PE"], index= ["CE", "PE"].index(trade_to_edit["CE/PE"]))
                edited_trade["Entry Price"] = col1.text_input("Entry Price", value=trade_to_edit["Entry Price"])
                edited_trade["Exit Price"] = col1.text_input("Exit Price", value=trade_to_edit["Exit Price"])
                edited_trade["Lot Size"] = col2.number_input("Lot Size", value=trade_to_edit["Lot Size"])
                edited_trade["Quantity"] = col2.number_input("Quantity", value=trade_to_edit["Quantity"], step=1)
                edited_trade["Confidence Level"] = col2.number_input("Confidence Level", min_value=1, max_value=5, step=1, value=trade_to_edit["Confidence Level"])
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

if __name__ == "__main__":
    main()
