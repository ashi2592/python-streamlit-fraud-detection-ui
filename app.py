import streamlit as st
import pandas as pd

st.title("Transaction and Customer Data Management")

st.write("Upload your .xlsx or .csv file to get started.")

def run_reconciliation_engine(data):
    """
    Mock reconciliation engine that returns the same dataset.
    """
    return data

def read_data(file):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        # Drop the last column
        df = df.iloc[:, :-1]
        return df
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

uploaded_file = st.file_uploader(
    "Choose a file",
    type=['csv', 'xlsx']
)

if uploaded_file is not None:
    df = read_data(uploaded_file)
    if df is not None:
        st.session_state.df = df
        # When a new file is uploaded, reset the editor state
        if 'data_editor_df' in st.session_state:
            del st.session_state['data_editor_df']
        st.success("File read successfully!")

if 'df' in st.session_state:
    if "data_editor_df" not in st.session_state:
        st.session_state.data_editor_df = st.session_state.df.copy()
        if 'final' not in st.session_state.data_editor_df.columns:
            st.session_state.data_editor_df['final'] = False
        st.session_state.data_editor_df.insert(0, 'select', False)

    st.write("### Transaction Data")
    st.info("You can edit data, and use the 'select' column to choose rows for actions.")

    # --- Pagination ---
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 0

    rows_per_page = 10
    start_idx = st.session_state.page_number * rows_per_page
    end_idx = start_idx + rows_per_page

    paginated_df = st.session_state.data_editor_df.iloc[start_idx:end_idx]

    edited_df_page = st.data_editor(paginated_df, key="data_editor", num_rows="dynamic")

    # Update the main dataframe with the edits from the current page
    st.session_state.data_editor_df.update(edited_df_page)


    # --- Pagination Controls ---
    col1, col2, col3 = st.columns([1, 1, 8])

    with col1:
        if st.button("Previous"):
            if st.session_state.page_number > 0:
                st.session_state.page_number -= 1
                st.rerun()

    with col2:
        if st.button("Next"):
            if end_idx < len(st.session_state.data_editor_df):
                st.session_state.page_number += 1
                st.rerun()

    st.write(f"Page {st.session_state.page_number + 1} of {len(st.session_state.data_editor_df) // rows_per_page + 1}")


    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Remove Selected Rows"):
            selected_rows = st.session_state.data_editor_df[st.session_state.data_editor_df['select']]
            if not selected_rows.empty:
                st.session_state.data_editor_df = st.session_state.data_editor_df[~st.session_state.data_editor_df['select']].copy()
                st.session_state.data_editor_df['select'] = False
                st.rerun()
            else:
                st.warning("No rows selected for removal.")

    with col2:
        if st.button("Mark Selected as Final"):
            selected_rows = st.session_state.data_editor_df[st.session_state.data_editor_df['select']]
            if not selected_rows.empty:
                # Use .loc to avoid SettingWithCopyWarning
                indices_to_update = st.session_state.data_editor_df[st.session_state.data_editor_df['select']].index
                st.session_state.data_editor_df.loc[indices_to_update, 'final'] = True
                st.session_state.data_editor_df['select'] = False
                st.rerun()
            else:
                st.warning("No rows selected to mark as final.")

    with col3:
        if st.button("Run Engine"):
            st.session_state.reconciled_df = run_reconciliation_engine(st.session_state.data_editor_df)
            st.session_state.run_engine = True
            st.rerun()

    # Update the main df without the select column
    st.session_state.df = st.session_state.data_editor_df.drop(columns=['select'], errors='ignore')

    # --- Reconciliation Results ---
    if st.session_state.get('run_engine'):
        st.write("### Reconciliation Results")
        if 'fraud' not in st.session_state.reconciled_df.columns:
            st.session_state.reconciled_df['fraud'] = False

        edited_reconciled_df = st.data_editor(st.session_state.reconciled_df, key="reconciliation_editor")
        st.session_state.reconciled_df = edited_reconciled_df

    # --- Export Fraudulent Transactions ---
    if st.session_state.get('run_engine'):
        st.write("### Export Fraudulent Transactions")
        fraudulent_df = st.session_state.reconciled_df[st.session_state.reconciled_df['fraud'] == True]

        if not fraudulent_df.empty:
            st.write("The following transactions are marked as fraudulent and will be exported:")
            st.dataframe(fraudulent_df.drop(columns=['fraud']))

            export_format = st.radio("Select export format:", ('.csv', '.xlsx'), key='export_format_fraud', horizontal=True)

            col1, _ = st.columns([1, 4])
            with col1:
                if export_format == '.csv':
                    csv = fraudulent_df.to_csv(index=False)
                    st.download_button(
                        label="Export to CSV",
                        data=csv,
                        file_name='fraudulent_transactions.csv',
                        mime='text/csv',
                    )
                else:
                    from io import BytesIO
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        fraudulent_df.to_excel(writer, index=False, sheet_name='Fraudulent Transactions')

                    st.download_button(
                        label="Export to XLSX",
                        data=output.getvalue(),
                        file_name='fraudulent_transactions.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
        else:
            st.info("No transactions marked as fraudulent to export.")
