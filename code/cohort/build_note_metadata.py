#!/usr/bin/env python
# coding: utf-8

# ## Workflow to Generate Metadata for the clinical notes

# In[1]:


import pandas as pd
unique = pd.read_csv("E:/mombaby-ehr-nlp-master/reports/cohort/infant_feeding_unique_ids.csv")
infant = pd.read_csv("E:/mombaby-ehr-nlp-master/reports/cohort/infant_feeding_note_ids.csv", delimiter = "\t")
raw = pd.read_csv("E:/mombaby-ehr-nlp-master/reports/cohort/notes_details.csv")


# In[3]:



infant_ready = infant.rename(columns={'part_id': 'part_id_tmp'})
#Creates a new column called 'files' by concatenating the values of 'part_id_tmp', '_', and the note_id column after replacing 'Note-' with an empty string using pandas string method str.replace()
infant_ready["files"] = infant_ready["part_id_tmp"] + "_" + infant_ready["note_id"].str.replace("Note-","") + ".txt"
#Creates a new column called 'part_id' by concatenating the string 'Baby-' with the 'part_id_tmp' column after removing the prefix 'Baby-' from it and converting it to integer and then converting it back to string
infant_ready["part_id"] = "Baby-" + infant_ready["part_id_tmp"].str.replace("Baby-","").astype(int).astype(str)
#Drops the 'part_id_tmp' column from the DataFrame
infant_ready = infant_ready.drop(["part_id_tmp"], axis=1)
#Creates a new column called 'unique_id' by concatenating the values of 'part_id' and 'note_id' column
infant_ready["unique_id"] = infant_ready["part_id"] + "_" + infant_ready["note_id"]
#Reorder the columns by moving the columns 'files' and 'part_id' to the front of the DataFrame and all other columns
infant_ready = infant_ready[["files", "part_id"] + [col for col in infant_ready if col not in ["files", "part_id"]]]
#Creating new variable infant_files as the column files from infant_ready DataFrame
infant_files = infant_ready['files']
infant_part = infant_ready['part_id'].unique()


# In[33]:


infant_part


# In[20]:


# Create a new column called 'files' by concatenating the values of 'Baby-Id' column after converting it to string, '', and the 'deid_note_ID' column after replacing 'NOTE' with an empty string
raw_ready = raw.assign(files = raw['Baby-Id'].astype(str) + '_' + raw['deid_note_ID'].str.replace('NOTE_','') + '.txt')
#Rename the column 'Baby-Id' to 'part_id_tmp'
raw_ready = raw_ready.rename(columns={'Baby-Id':'part_id_tmp'})
# Create a new column called 'note_file_path' by concatenating the string '/blue/djlemas/share/data/MyEHR/5year_dataset/clinical_notes/raw_data2_528K/unzip_all_528K/' with the 'deid_note_ID' column after converting it to string
raw_ready = raw_ready.assign(note_file_path = '/blue/djlemas/share/data/MyEHR/5year_dataset/clinical_notes/raw_data2_528K/unzip_all_528K/' + raw_ready['deid_note_ID'].astype(str) + '_.txt',note_file_name = raw_ready['deid_note_ID'].astype(str) + '_.txt')
# Create a new column called 'note_file_name' by concatenating the 'deid_note_ID' column after converting it to string
raw_ready = raw_ready.assign(note_id = raw['deid_note_ID'].str.replace('NOTE_','Note-'))
# Create a new column called 'note_id' by replacing 'NOTE_' with 'Note-' in 'deid_note_ID' column
raw_ready = raw_ready.assign(part_id = 'Baby-' + raw_ready['part_id_tmp'].str.replace('Baby-','').astype(int).astype(str))
#Create a new column called 'part_id' by concatenating 'Baby-' with the 'part_id_tmp' column after removing the prefix 'Baby-' from it and converting it to integer and then converting it back to string
raw_ready = raw_ready.assign(unique_id = raw_ready['part_id'] + '_' + raw_ready['note_id'])
#Create a new column called 'unique_id' by concatenating the values of 'part_id' and 'note_id' column
raw_ready = raw_ready[['files'] + [col for col in raw_ready.columns if col not in ['files','part_id_tmp']]]


# In[23]:


raw_ready


# In[24]:


#Use the built-in python set intersection() method to get the common elements in the two sets 
#Calculate the length of the set obtained 
len(set(raw_ready['part_id']).intersection(set(infant_ready['part_id'])))


# In[25]:


raw_ready['part_id']


# In[28]:


#Create a new column called part_match in the raw_ready
#Check for each value of the 'part_id' column in the raw_ready dataframe if it's present in the infant_part

raw_annotate = raw_ready.assign(part_match = (raw_ready['part_id'].isin(infant_part)).astype(int))


# In[29]:


raw_annotate


# In[30]:


raw_annotate['part_match'].value_counts()


# In[36]:



file_name = "rawdata_note_annotated_v0.csv"
data_directory = "E:/mombaby-ehr-nlp-master/reports/cohort/"


# In[37]:


data_path = data_directory + file_name


# In[39]:


#export file to the above patbh
raw_annotate.to_csv(data_path, sep='\t', index=False)


# In[ ]:





# In[40]:


#reate a new dataframe note by adding new columns 'files_tmp' and 'part_id_tmp' to raw_annotate dataframe.
#Split the 'files_tmp' column
note = raw_annotate.assign(files_tmp = raw_annotate['files'],
                           part_id_tmp = raw_annotate['part_id'])
note[['part_id','drop']] = note['files_tmp'].str.split('_',expand=True)
#Drops the 'drop' and 'files_tmp' columns from the 'note' dataframe 
note = note.drop(columns=['drop','files_tmp'])


# In[41]:


#import DOB
births = pd.read_csv("E:/mombaby-ehr-nlp-master/reports/cohort/baby_dob.csv")
births = births[births['redcap_repeat_instrument'] == "baby_demography"]
births = births[['part_id','baby_dob']]


# In[43]:


# merge codes --> births.
births_datetime = note.merge(births,on='part_id',how='left')
births_datetime['days2birth'] = (pd.to_datetime(births_datetime['note_created_datetime']) - pd.to_datetime(births_datetime['baby_dob'])).dt.days
births_datetime['prenatal'] = (births_datetime['days2birth'] < -1).astype(int)
births_datetime['delivery'] = ((births_datetime['days2birth'] > -1) & (births_datetime['days2birth'] < 1)).astype(int)
births_datetime['postnatal'] = (births_datetime['days2birth'] > 1).astype(int)


# In[44]:


file_name = "rawdata_876K_note_annotated_v0.csv"
data_directory = "E:/mombaby-ehr-nlp-master/reports/cohort/"
data_path = data_directory + file_name


# In[45]:


births_datetime.to_csv(data_path, sep='\t', index=False)


# In[46]:


births_datetime


# In[48]:


# subset to those with codes of interest
infantfeeding_746_notes = births_datetime[births_datetime['part_match'] == 1]
len(infantfeeding_746_notes['part_id'].unique())


# In[49]:


# Raw Files Ready (metadata)
file_name = "infantfeeding_746_notes_v0.csv"
data_directory = "E:/mombaby-ehr-nlp-master/reports/cohort/"
data_path = data_directory + file_name


# In[50]:


infantfeeding_746_notes.to_csv(data_path, sep='\t', index=False)


# In[51]:


file_746 = infantfeeding_746_notes[['note_file_path']]


# In[52]:


file_746


# In[53]:


file_name = "infantfeeding_746_filenames_v0.csv"
data_directory = "E:/mombaby-ehr-nlp-master/reports/cohort/"
data_path = data_directory + file_name


# In[54]:


file_746.to_csv(data_path, sep='\t', index=False)


# In[58]:


classes = pd.read_csv("E:/mombaby-ehr-nlp-master/reports/cohort/note_details_18K.csv")


# In[67]:


classes


# In[65]:


meta = pd.read_csv("E:/mombaby-ehr-nlp-master/reports/cohort/infantfeeding_746_notes_v0.csv")


# In[66]:


meta


# In[68]:



classes = classes.rename(columns={'file_name':'note_file_name'})


# In[69]:


classes


# In[70]:


# Merge two dataframs with filename in common
metadata = classes.merge(meta,on='note_file_name',how='left')


# In[71]:


metadata


# In[72]:


file_name = "infantfeeding_18k_files_metadata.csv"
data_directory = "E:/mombaby-ehr-nlp-master/reports/cohort/"
data_path = data_directory + file_name


# In[73]:


#export final metadata file
metadata.to_csv(data_path, sep='\t', index=False)


# In[ ]:




