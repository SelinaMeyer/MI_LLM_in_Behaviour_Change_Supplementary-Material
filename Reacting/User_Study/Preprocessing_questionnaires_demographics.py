import pandas as pd
import numpy as np
import os

user = pd.read_csv("Main_Study/user.csv", sep=";")
user = user[user["attention_check"] == "Stimme überhaupt nicht zu"]
user = user.drop(columns="general_remarks")
chats = pd.read_csv("Main_Study/annotated/chat_annotated.csv")
turns = pd.read_csv("Main_Study/annotated/turns_with_context/Blatt 1-turns_with_context.csv")

# valence_new,label_new,sublabel_new,code
turn_classifications = pd.read_csv("Main_Study/annotated/turns_reclassified_with_prefilter_context.csv")

directory_path = 'Main_Study/demographics'

# Initialize an empty list to store DataFrames
dataframes = []

# Loop through the files in the directory
for filename in os.listdir(directory_path):
    if filename.endswith(".csv"):
        # Create the full file path
        file_path = os.path.join(directory_path, filename)
        
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        
        # Append the DataFrame to the list
        dataframes.append(df)

# Concatenate all the DataFrames in the list into one
user_demographics = pd.concat(dataframes, ignore_index=True)

user_demographics = user_demographics[["Submission id", "Participant id", "Time taken", "Total approvals", "Age", "Sex"]].copy()
user_demographics.rename(columns={"Participant id": "user_id"}, inplace=True)
user_demographics["Time taken"] = user_demographics["Time taken"]/60

user_merged = pd.merge(user, user_demographics, on="user_id", how="left")
user_merged = user_merged.drop_duplicates(subset="user_id")
user_merged.replace("DATA_EXPIRED", np.nan, inplace=True)

columns_to_replace = ["wai_sr_1", "wai_sr_2", "wai_sr_3", "wai_sr_4", "wai_sr_5", "wai_sr_6",
                      "wai_sr_7", "wai_sr_8", "wai_sr_9", "wai_sr_10", "wai_sr_11", "wai_sr_12"]

# Define the mapping of strings to numerical values
replace_dict = {"selten": 1, "manchmal": 2, "öfters": 3, "sehr oft": 4, "immer": 5}

# Loop through the columns and replace the values
for col in columns_to_replace:
    user_merged[col] = user_merged[col].replace(replace_dict)


ues_pos_cols = ["fa_s1","fa_s2","fa_s3", "rw_s1","rw_s2","rw_s3", "pe_1","pe_2","pe_3", "cc_1","cc_2","cc_3",
                "cc_4"]
pos_dict = {"Stimme überhaupt nicht zu":1,
                                     "Stimme eher nicht zu":2,
                                     "Stimme weder zu noch ab":3,
                                     "Stimme eher zu":4,
                                     "Stimme voll und ganz zu":5}

for col in ues_pos_cols:
    user_merged[col] = user_merged[col].replace(pos_dict)

neg_cols = ["pu_s1","pu_s2","pu_s3"]
neg_dict = {"Stimme überhaupt nicht zu":5,
                                     "Stimme eher nicht zu":4,
                                     "Stimme weder zu noch ab":3,
                                     "Stimme eher zu":2,
                                     "Stimme voll und ganz zu":1}

for col in neg_cols:
    user_merged[col] = user_merged[col].replace(neg_dict)


pm_pos_cols = ["pm_1", "pm_3", "pm_4", "pm_6", "pm_7", "pm_8", "pm_10", "pm_11"]
pos_dict = {"überhaupt nicht": 1,
            "ein wenig":2,
            "manchmal":3,
            "sehr viel":4,
            "immer":5}

for col in pm_pos_cols:
    user_merged[col] = user_merged[col].replace(pos_dict)

neg_cols = ["pm_2", "pm_5", "pm_9"]
neg_dict = {"überhaupt nicht": 5,
            "ein wenig":4,
            "manchmal":3,
            "sehr viel":2,
            "immer":1}

for col in neg_cols:
    user_merged[col] = user_merged[col].replace(neg_dict)


user_merged["Therapeutic Alliance"] = user_merged[["wai_sr_1", "wai_sr_2", "wai_sr_3", "wai_sr_4", "wai_sr_5", "wai_sr_6",
                      "wai_sr_7", "wai_sr_8", "wai_sr_9", "wai_sr_10", "wai_sr_11", "wai_sr_12"]].mean(axis=1)

user_merged["User Engagement"] = user_merged[["fa_s1","fa_s2","fa_s3", "rw_s1","rw_s2","rw_s3", "pu_s1","pu_s2","pu_s3"]].mean(axis=1)
user_merged["Perception of MI"] = user_merged[["pm_1", "pm_2", "pm_3", "pm_4", "pm_5", "pm_6", "pm_7", "pm_8", "pm_9", "pm_10", "pm_11"]].sum(axis=1)

user_merged["Perception MI Inadherent"] = 15 - user_merged[["pm_2", "pm_5", "pm_9"]].sum(axis=1)
user_merged["Perceived Empathy"] = user_merged[["pe_1","pe_2","pe_3"]].mean(axis=1)
user_merged["Communication Competence"] = user_merged[["cc_1","cc_2","cc_3", "cc_4"]].mean(axis=1)

user_merged["Readiness to Change (Delta)"] = user_merged["readiness_to_change_end"] - user_merged["readiness_to_change_start"]
user.loc[user['user_id'] == "627e030cc712893d578971f5", ['identification_with_goal',
       'current_pursuit_of_target', 'readiness_to_change_start',
       'readiness_to_change_end', 'Readiness to Change (Delta)']] = np.nan # user message


# based on https://www.nd.gov.hk/pdf/bdf-2010R2-q13-eng.pdf
user_merged.loc[user_merged["readiness_to_change_start"] <= 3, "stage"] = "precontemplation"
user_merged.loc[(user_merged["readiness_to_change_start"] >= 4) & (user_merged["readiness_to_change_start"] <= 6) , "stage"] = "contemplation"
user_merged.loc[(user_merged["readiness_to_change_start"] >= 7) & (user_merged["readiness_to_change_start"] <= 8) , "stage"] = "preparation"
user_merged.loc[user_merged["readiness_to_change_start"] == 9, "stage"] = "action"
user_merged.loc[user_merged["readiness_to_change_start"] == 10, "stage"] = "maintenance"

chats = chats[~chats.user_id.str.contains("_")]
chats = chats[~chats["target_behaviour"].isin(["sein Verhalten ändern"])]

gesund = chats.user_id[chats["target_behaviour"].isin(["gesünder essen"])].tolist()
prokrastinieren = chats.user_id[chats["target_behaviour"].isin(["weniger prokrastinieren"])].tolist()
nachhaltig = chats.user_id[chats["target_behaviour"].isin(["nachhaltiger leben"])].tolist()

chats.drop(columns="harmful", inplace=True)

harmful_counts = turns.groupby('chat_id')['harmful'].sum()
chats = chats.merge(harmful_counts, on='chat_id', how='left')

rating_counts = turns.pivot_table(index='chat_id', columns='user_rating', aggfunc='size', fill_value=0)
valence_counts = turn_classifications.pivot_table(index='chat_id', columns='valence_new', aggfunc='size', fill_value=0)
label_counts = turn_classifications.pivot_table(index='chat_id', columns='label_new', aggfunc='size', fill_value=0)
sublabel_counts = turn_classifications.pivot_table(index='chat_id', columns='sublabel_new', aggfunc='size', fill_value=0)
code_counts = turn_classifications.pivot_table(index='chat_id', columns='code', aggfunc='size', fill_value=0)


# Step 3: Prepare the Counts for Merging
# Ensure the resulting dataframe is structured properly for merging
rating_counts.reset_index(inplace=True)

# Step 4: Merge with the Chats DataFrame
chats = chats.merge(rating_counts, on='chat_id', how='left')
chats = chats.merge(valence_counts, on='chat_id', how='left')
chats = chats.merge(label_counts, on='chat_id', how='left')
chats = chats.merge(sublabel_counts, on='chat_id', how='left')
chats = chats.merge(code_counts, on='chat_id', how='left')

user_merged["target_behaviour"] = ""

user_merged.loc[user_merged["user_id"].isin(gesund), "target_behaviour"] = "gesünder essen"
user_merged.loc[user_merged["user_id"].isin(prokrastinieren), "target_behaviour"] = "weniger prokrastinieren"
user_merged.loc[user_merged["user_id"].isin(nachhaltig), "target_behaviour"] = "nachhaltiger leben"

user_merged = pd.merge(user_merged, chats[["user_id", "chat_id", "Cooperative", "Reflective", 
                                  "Pre-informed/finds own solution", "Contained technical issue" ,"harmful", 
                                  "gut/hilfreich", "schlecht/unpassend", 'change', 
                                  'Follow/Neutral', 'sustain', 'Reason', 'Commitment', 'Taking Steps',
                                  'desire','General Reason', 'ability', 'need', 'Rd+', 'FN', 'R_+', 'C+', 
                                  'Ra+', 'R_-', 'TS-', 'TS+', 'Rd-', 'Ra-',
                                  'Rn+', 'Rn-', 'C-']], on="user_id", how="left")

user_merged.to_csv("Consolidated_Data/user_preprocessed_with_demographics.csv")