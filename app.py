import streamlit as st
import pandas as pd

st.title("Transaction and Customer Data Management")

st.write("Upload your .xlsx or .csv file to get started.")

def read_data(file):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
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

    edited_df = st.data_editor(st.session_state.data_editor_df, key="data_editor", num_rows="dynamic")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Remove Selected Rows"):
            selected_rows = edited_df[edited_df['select']]
            if not selected_rows.empty:
                st.session_state.data_editor_df = edited_df[~edited_df['select']].copy()
                st.session_state.data_editor_df['select'] = False
                st.rerun()
            else:
                st.warning("No rows selected for removal.")

    with col2:
        if st.button("Mark Selected as Final"):
            selected_rows = edited_df[edited_df['select']]
            if not selected_rows.empty:
                # Use .loc to avoid SettingWithCopyWarning
                indices_to_update = edited_df[edited_df['select']].index
                st.session_state.data_editor_df.loc[indices_to_update, 'final'] = True
                st.session_state.data_editor_df['select'] = False
                st.rerun()
            else:
                st.warning("No rows selected to mark as final.")

    # Update the main df without the select column
    st.session_state.df = st.session_state.data_editor_df.drop(columns=['select'], errors='ignore')

    # -- Export functionality --
    st.write("### Export Finalized Transactions")
    finalized_df = st.session_state.df[st.session_state.df['final'] == True]

    if not finalized_df.empty:
        st.write("The following transactions are marked as final and will be exported:")
        st.dataframe(finalized_df.drop(columns=['final'])) # Don't show the 'final' column in the export preview

        export_format = st.radio("Select export format:", ('.csv', '.xlsx'), key='export_format', horizontal=True)

        col1, _ = st.columns([1, 4])
        with col1:
            if export_format == '.csv':
                csv = finalized_df.to_csv(index=False)
                st.download_button(
                    label="Export to CSV",
                    data=csv,
                    file_name='finalized_transactions.csv',
                    mime='text/csv',
                )
            else:
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    finalized_df.to_excel(writer, index=False, sheet_name='Finalized Transactions')

                st.download_button(
                    label="Export to XLSX",
                    data=output.getvalue(),
                    file_name='finalized_transactions.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
    else:
        st.info("No transactions marked as final to export.")
