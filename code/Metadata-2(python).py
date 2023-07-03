import pandas as pd

# Read the 'metadata_prenatal_400k_v1.csv' file into a DataFrame called 'meta'
meta = pd.read_csv("metadata_prenatal_400k_v1.csv")

# Display the 'meta' DataFrame
meta

# Modify the 'file_name' column in the 'meta' DataFrame to extract the 'note_id'
meta['note_id'] = meta['file_name'].str.replace('_.txt', '')

# Display the updated 'meta' DataFrame
meta

# Read the 'mom_notes_prenatal_visit.csv' file into a DataFrame called 'm1'
m1 = pd.read_csv("mom_notes_prenatal_visit.csv")
# Rename the 'deid_note_ID' column to 'note_id'
m1 = m1.rename(columns={'deid_note_ID':'note_id'})

# Display the 'm1' DataFrame
m1

# Merge the 'meta' and 'm1' DataFrames based on the 'note_id' column
m2 = meta.merge(m1, on='note_id', how='left')
# Rename the 'Deidentified_mom_ID' column to 'deidentified_mom_id'
m2 = m2.rename(columns={'Deidentified_mom_ID':'deidentified_mom_id'})

# Display the merged DataFrame 'm2'
m2

# Drop rows with missing values in the 'note_created_datetime' column
m2 = m2.dropna(subset=['note_created_datetime'])

# Display the updated DataFrame 'm2'
m2

# Read the 'baby_mom_at_birth_with_payer.csv' file into a DataFrame called 'mom'
mom = pd.read_csv("baby_mom_at_birth_with_payer.csv")

# Display the 'mom' DataFrame
mom

# Merge the 'mom' and 'm2' DataFrames based on the 'deidentified_mom_id' column
prenatal_final = mom.merge(m2, on='deidentified_mom_id')

# Display the merged DataFrame 'prenatal_final'
prenatal_final

# Drop rows with missing values in the 'date_of_delivery' column
prenatal_final = prenatal_final.dropna(subset=['date_of_delivery'])

# Convert the columns 'date_of_delivery' and 'note_created_datetime' to datetime format
prenatal_final['date_of_delivery'] = pd.to_datetime(prenatal_final['date_of_delivery'], format='%m/%d/%Y %H:%M')
prenatal_final['note_created_datetime'] = pd.to_datetime(prenatal_final['note_created_datetime'])

# Calculate the difference between 'date_of_delivery' and 'note_created_datetime'
prenatal_final['days2birth'] = prenatal_final['date_of_delivery'] - prenatal_final['note_created_datetime']

# Display the updated DataFrame 'prenatal_final'
prenatal_final

# Convert the 'days2birth' column to Timedelta format
prenatal_final['days2birth'] = pd.to_timedelta(prenatal_final['days2birth'])

# Create a boolean mask to filter the DataFrame based on the desired range (-280 to 0 days)
mask = (prenatal_final['days2birth'] >= pd.Timedelta(days=-280)) & (prenatal_final['days2birth'] <= pd.Timedelta(days=0))

# Filter the DataFrame based on the boolean mask
df_filtered = prenatal_final[mask]

# Display the filtered DataFrame 'df_filtered'
df_filtered

# Count the number of duplicated note_id values
duplicate_counts = df_filtered['note_id'].duplicated().sum()

# Count the number of unique note_id values
unique_counts = df_filtered['note_id'].nunique()

# Display the counts
duplicate_counts
unique_counts

# Write the 'df_filtered' DataFrame to a CSV file named 'delivery_1000k_notes_metadata_v1.csv'
df_filtered.to_csv('prenatal_400k_notes_metadata_v1.csv', index=False)
