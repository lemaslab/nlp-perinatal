# Load required libraries
library(dplyr)
library(tidyverse)
library(stringr)
library(knitr)
library(tibble)
library(readr)
library(quanteda)
# Get the list of file names from a specific directory
files <- list.files(
  path = "/blue/djlemas/share/data/MyEHR/10year_dataset/notes/all_notes/prenatal/prenatal_all_notes/",
  pattern = ".txt",
  all.files = TRUE,
  full.names = FALSE
) %>% as_tibble() %>% 
  mutate(note_number = as.numeric(stringr::str_split(value, "_") %>% map_chr(., 2))) %>% 
  rename(file_name = value) %>% 
  add_column(
    char_count = NA,
    tokens = NA,
    sentences = NA,
    file_size = NA,
    breast = NA,
    bottle = NA,
    express = NA,
    smoking = NA,
    suicide = NA,
    pain = NA,
    Cancer = NA,
    diabetes = NA,
    hypertension = NA
)

# counter
file_name_vec <- files$file_name
files_loop <- files %>% filter(file_name %in% file_name_vec)

file_count <- length(file_name_vec)

# Define a dictionary of terms
my_dict <- dictionary(list(
  breast = c("breastfeeding", "breast"),
  bottle = c("bottle"),
  express = c("express", "pump"),
  smoking = c("smoking"),
  suicide = c("suicide", "self-harm"),
  pain = c("pain"),
  Cancer = c("cancer", "tumor"),
  diabetes = c("Diabetes", "Blood sugar", "insulin"),
  hypertension = c("Hypertension", "blood pressure")
))

# Loop through annotations
for (i in 1:file_count) {
  
   # Get the current file index and its path
  file_index <- file_name_vec[i]
  file_index_path <- paste0(
    "/blue/djlemas/share/data/MyEHR/10year_dataset/notes/all_notes/prenatal/prenatal_all_notes/",
    file_index
  )
  print(file_index)
  print(i)
  
  # note info
  file_size <- file.size(file_index_path)
  
  # EXTRACT DATA FROM TEXT FILE
  
  note <- read_file(file = file_index_path)  # Read the contents of the file
  
  # character count
  char_count <- nchar(note) # Count the number of characters in the note
  
  # quanteda package
  corpus <- corpus(note)  # build a new corpus from the texts
  
  # check if corpus has content
  if (ntoken(corpus) > 0) {
    names(corpus) <- file_index # Assign the file index as the name of the corpus
    sum <- summary(corpus)      # Calculate summary statistics for the corpus
    tokens <- sum[3]            # Get the token count
    sentence <- sum[4]          # Get the sentence count
    
    dat1 <- dfm(corpus, dictionary = my_dict)   # Create a document-feature matrix with the specified dictionary
    dat2 <- as_tibble(dat1)                     # Convert the document-feature matrix to a tibble
    
    breast <- dat2[2]
    bottle <- dat2[3]
    express <- dat2[4]
    smoking <- dat2[5]
    suicide <- dat2[6]
    pain <- dat2[7]
    Cancer <- dat2[8]
    diabetes <- dat2[9]
    hypertension <- dat2[10]
    
    # INSERT INTO TABLE
    files_loop[i, 3] <- char_count 
    files_loop[i, 4] <- tokens 
    files_loop[i, 5] <- sentence   
    files_loop[i, 6] <- file_size  
    files_loop[i, 7] <- breast
    files_loop[i, 8] <- bottle
    files_loop[i, 9] <- express
    files_loop[i, 10] <- smoking
    files_loop[i, 11] <- suicide
    files_loop[i, 12] <- pain
    files_loop[i, 13] <- Cancer
    files_loop[i, 14] <- diabetes
    files_loop[i, 15] <- hypertension
  } else {
    # skip to next iteration if corpus has no content
    next
  }
  
} # end loop

# remove special characters
files_final <- files_loop 
      
# export file
file_name <- paste0("metadata_prenatal_400k_v1.csv")
data_directory <- paste0("/blue/djlemas/share/data/MyEHR/10year_dataset/notes/all_notes/prenatal/") 
data_path <- paste0(data_directory, file_name)

# export
write_csv(files_loop, file = data_path, col_names = TRUE)
