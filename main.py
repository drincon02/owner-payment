import pandas as pd
import streamlit as st


def process_file(file_path, management_fee, date_field, payee_field):
    
    # Read the Excel file, skipping the first 10 rows
    df = pd.read_excel(file_path, skiprows=10)

    rent_accounts = [4100, 4105, 6091, 6147, 6171, 6173]

    expense_accounts = [6091, 6147, 6171, 6173]

    rent_only = [4100, 4105]

    df = df[df['Account Number'].isin(rent_accounts)]

    exclude_columns = ['Account Number', 'Account Name']

    melted_df = pd.melt(df, id_vars=exclude_columns, var_name='Bill Property Code', value_name='Amount')

    # Merge 'Account Number' and 'Account Name' columns into a new column 'Bill Account'
    melted_df = melted_df.assign(**{'Bill Account': melted_df['Account Number'].astype(str) + melted_df['Account Name']})

    melted_df.loc[melted_df['Account Number'].isin(expense_accounts), 'Amount'] *= -1

    # Add empty columns
    empty_columns = ['Bill Unit Name', 'Payee Name', 'Description', 'Bill Date', 'Due Date', 'Posting Date', 'Bill Reference', 'Bill Remarks', 'Memo For Check', 'Purchase Order Number']
    melted_df = melted_df.assign(**{col: '' for col in empty_columns})


    melted_df['management_fee'] = management_fee
    melted_df["Payee Name"] = payee_field
    melted_df["Bill Date"] = date_field
    melted_df["Due Date"] = date_field
    melted_df["Posting Date"] = date_field

    melted_df["Management Fee"] = melted_df["management_fee"] * melted_df["Amount"]

    management_fee_account = "4900: Management Fees Income"


    # Create a new row with the specified values
    for x in melted_df["Bill Property Code"].unique():
        
        # Filter the DataFrame and sum the "Amount" column
        sum_amount = melted_df.loc[(melted_df['Bill Property Code'] == x) & (melted_df['Account Number'].isin(rent_only)), 'Amount'].sum()
        management_fee_amount = -sum_amount * management_fee

        new_row = pd.DataFrame({'Bill Account': [management_fee_account],
                            'Bill Property Code': [x],
                            'Amount': [management_fee_amount],
                            'Bill Unit Name': [''],
                            'Payee Name': [payee_field],
                            'Description': [''],
                            'Bill Date': [date_field],
                            'Due Date': [date_field],
                            'Posting Date': [date_field],
                            'Bill Reference': ['1'],
                            'Bill Remarks': [''],
                            'Memo For Check': [''],
                            'Purchase Order Number': ['']})

        # Concatenate the new row to the original DataFrame
        melted_df = pd.concat([melted_df, new_row], ignore_index=True)

    
    # Drop the individual 'Account Number' and 'Account Name' columns if needed
    melted_df = melted_df.drop(['Account Number', 'Account Name', 'management_fee', 'Management Fee'], axis=1)

    melted_df["Bill Reference"] = "1"

    
    return melted_df

def main():
    st.title("Owner Payment")

    # File Upload
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    
    # Input field for management_fee
    management_fee = st.number_input("Enter Management Fee", value=0.03, step=0.01)

    bill_date = st.date_input("Bill Date")
    payee_name = st.text_input("Payee Name")

    if uploaded_file is not None:
        # Process the file
        df = process_file(uploaded_file, management_fee, bill_date, payee_name)

        # Display processed data
        st.write("Original DataFrame:")
        st.write(df)

        # Example: Add processing steps here
        # ...

        # Save the processed DataFrame to a CSV file
        st.markdown("### Download Processed Data")
        st.button("Download CSV", on_click=lambda: download_csv(df))

def download_csv(df):
    # Save DataFrame to CSV
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="processed_data.csv",
        key="download_button",
    )

if __name__ == "__main__":
    main()
