import psycopg2

conn_details = psycopg2.connect(
            host="localhost",
            database="Testbase",
            user="postgres",
            password="",
            port="5432"
            )
"""
conn_details = psycopg2.connect(
            host="132.199.138.79",
            database="selina",
            user="mehrsprachigkeit",
            password="doing-quote-moody",
            port="5432"
            )"""

cursor = conn_details.cursor()

user_stmt = """CREATE TABLE IF NOT EXISTS "user" (user_id TEXT PRIMARY KEY,
                                                    start_time TIMESTAMP,
                                                    end_time TIMESTAMP,
                                                    condition TEXT,
                                                    education TEXT,
                                                    job TEXT,
                                                    identification_with_goal INTEGER,
                                                    current_pursuit_of_target INTEGER,
                                                    readiness_to_change_start INTEGER,
                                                    readiness_to_change_end INTEGER,
                                                    WAI_SR_1 TEXT,
                                                    WAI_SR_2 TEXT,
                                                    WAI_SR_3 TEXT,
                                                    WAI_SR_4 TEXT,
                                                    WAI_SR_5 TEXT,
                                                    WAI_SR_6 TEXT,
                                                    WAI_SR_7 TEXT,
                                                    WAI_SR_8 TEXT,
                                                    WAI_SR_9 TEXT,
                                                    WAI_SR_10 TEXT,
                                                    WAI_SR_11 TEXT,
                                                    WAI_SR_12 TEXT,
                                                    FA_S1 TEXT,
                                                    FA_S2 TEXT,
                                                    FA_S3 TEXT, 
                                                    PU_S1 TEXT, 
                                                    PU_S2 TEXT,
                                                    PU_S3 TEXT,
                                                    RW_S1 TEXT,
                                                    RW_S2 TEXT,
                                                    RW_S3 TEXT,
                                                    PM_1 TEXT,
                                                    PM_2 TEXT,
                                                    PM_3 TEXT,
                                                    PM_4 TEXT,
                                                    PM_5 TEXT,
                                                    PM_6 TEXT,
                                                    PM_7 TEXT,
                                                    PM_8 TEXT,
                                                    PM_9 TEXT, 
                                                    PM_10 TEXT,
                                                    PM_11 TEXT,
                                                    CC_1 TEXT, 
                                                    CC_2 TEXT,
                                                    CC_3 TEXT,
                                                    CC_4 TEXT,
                                                    PE_1 TEXT,
                                                    PE_2 TEXT,
                                                    PE_3 TEXT,
                                                    general_remarks TEXT,
                                                    attention_check TEXT)"""
print(user_stmt)
cursor.execute(user_stmt)
conn_details.commit()
        
chat_stmt = """CREATE TABLE IF NOT EXISTS "chat" (chat_id SERIAL PRIMARY KEY,
                                                    date TIMESTAMP,
                                                    user_id TEXT,
                                                    target_behaviour TEXT,
                                                    num_turns INTEGER, 
                                                    change_talk_ratio FLOAT,
                                                    top_utterance_type TEXT)"""
print(chat_stmt)
cursor.execute(chat_stmt)
conn_details.commit()
        
turn_stmt = """CREATE TABLE IF NOT EXISTS "turn" (utterance_id SERIAL PRIMARY KEY,
                                                    turn_id INTEGER,
                                                    chat_id INTEGER,
                                                    datetime TIMESTAMP,
                                                    user_utterance TEXT,
                                                    valence TEXT,
                                                    valence_score FLOAT,
                                                    label TEXT, 
                                                    label_score FLOAT,
                                                    sublabel TEXT,
                                                    sublabel_score FLOAT,
                                                    bot_action TEXT,
                                                    bot_datetime TIMESTAMP,
                                                    bot_utterance TEXT,
                                                    user_rating TEXT,
                                                    user_rating_explanation TEXT)"""
print(turn_stmt)
cursor.execute(turn_stmt)
conn_details.commit()

cursor.close()
conn_details.close