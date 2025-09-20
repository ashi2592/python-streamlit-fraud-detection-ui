# python-streamlit-fraud-detection-ui


Epic: File Upload and Transaction Management
User Story 1: Upload Files

As a user,
I want to upload .xlsx or .csv files containing transaction and customer data,
so that I can process and analyze them in the application.

✅ Acceptance Criteria

The system should support .xlsx and .csv file formats.

Users should be able to upload files via the Streamlit UI.

Uploaded files should be validated (correct format, readable).

If the file is invalid, the system should display an error message.

User Story 2: Read File Data

As a user,
I want the system to read and parse the uploaded file data,
so that I can view the transaction and customer details.

✅ Acceptance Criteria

The system should read the file and extract transaction and customer records.

Data should be stored in memory for further processing.

Errors in reading/parsing should be clearly shown to the user.

User Story 3: Display and Manage Data in UI

As a user,
I want to see a table of transactions and related customers in the UI,
so that I can review the data and make corrections.

✅ Acceptance Criteria

The UI should display a table with transaction details and customer info.

Each row should have a checkbox or selection option.

Users should be able to manually remove rows.

Users should be able to mark selected rows as "final."

User Story 4: Export Selected Transactions

As a user,
I want to export only the selected (final) transactions into a new file,
so that I can save and use the filtered data.

✅ Acceptance Criteria

The system should allow exporting selected transactions.

The output file should be downloadable in .xlsx or .csv format.

Only rows marked as "final" should be included.

The file should include both transaction and customer details.
