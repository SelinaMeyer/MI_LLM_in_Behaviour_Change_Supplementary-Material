import psycopg2
from psycopg2 import extensions
import datetime
from collections import Counter

class DBHelper:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            database="Testbase",
            user="postgres",
            password="",
            port="5432",
            )
        '''self.conn = psycopg2.connect(
            host="132.199.138.79",
            database="selina",
            user="mehrsprachigkeit",
            password="doing-quote-moody",
            port="5432"
            )'''
       #self.conn.set_isolation_level(extensions.ISOLATION_LEVEL_READ_COMMITTED)
        #print("isolation level:", self.conn.isolation_level)
        
    def add_user(self, user_id, condition, start_time):
        try:
            with self.conn.cursor() as cursor:
                stmt = """INSERT INTO \"user\" (user_id, condition, start_time) 
                        VALUES (%s, %s, %s)"""
                args = (user_id, condition, start_time)
                print("New User added", args)
                cursor.execute(stmt, args)
            self.conn.commit()
            #print(args)
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error occurred while adding user {user_id}:", e)
    
    def add_scale_item(self, user_id, item, response=None):
        try: 
            with self.conn.cursor() as cursor:
                stmt = f"UPDATE \"user\" SET {item} = (%s) WHERE user_id=(%s)"
                args = (response, user_id)
                cursor.execute(stmt, args)
            self.conn.commit()
            #print(args)
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error occurred while adding scale item {item} with response {response} to user {user_id}:", e)
    
    def add_post_test(self, identification, change_pref, readiness, user_id):
        try: 
            with self.conn.cursor() as cursor:
                stmt = """UPDATE \"user\" SET identification_with_goal=(%s), current_pursuit_of_target=(%s), 
                readiness_to_change_end=(%s) WHERE user_id=(%s)"""
                args = (identification, change_pref, readiness, user_id)
                #print(args)
                cursor.execute(stmt, args)
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"""Error occurred while adding scale item identification_with_goal = {identification},
                  current_pursuit_of_target = {change_pref}, and readiness_to_change_end = {readiness} to user_id={user_id}""", e)

    def add_ta(self, ta1, ta2, ta3, ta4, ta5, ta6, ta7, ta8, ta9, ta10, ta11, ta12, user_id):
        try:
            with self.conn.cursor() as cursor:
                stmt = """UPDATE \"user\" SET WAI_SR_1=(%s), WAI_SR_2=(%s), WAI_SR_3=(%s), WAI_SR_4=(%s),
                WAI_SR_5=(%s), WAI_SR_6=(%s), WAI_SR_7=(%s), WAI_SR_8=(%s), WAI_SR_9=(%s), WAI_SR_10=(%s), WAI_SR_11=(%s),
                WAI_SR_12=(%s) WHERE user_id=(%s)"""
                args = (ta1, ta2, ta3, ta4, ta5, ta6, ta7, ta8, ta9, ta10, ta11, ta12, user_id)
                cursor.execute(stmt, args)
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"""Error occured while adding WAI_SR with values: WAI_SR_1={ta1}, WAI_SR_2={ta2}, WAI_SR_3={ta3}, WAI_SR_4=(%s),
                WAI_SR_5={ta5}, WAI_SR_6={ta6}, WAI_SR_7={ta7}, WAI_SR_8={ta8}, WAI_SR_9={ta9}, WAI_SR_10={ta10}, WAI_SR_11={ta11},
                WAI_SR_12={ta12} to user {user_id}""")
            
    def add_ues(self, FA_S1, FA_S2, FA_S3, PU_S1, PU_S2, PU_S3, RW_S1, RW_S2, RW_S3, attention, user_id):
        try:
            with self.conn.cursor() as cursor:
                stmt = """UPDATE \"user\" SET FA_S1=(%s), FA_S2=(%s), FA_S3=(%s), PU_S1=(%s),
                PU_S2=(%s), PU_S3=(%s), RW_S1=(%s), RW_S2=(%s), RW_S3=(%s), attention_check=(%s) 
                WHERE user_id=(%s)"""
                args = (FA_S1, FA_S2, FA_S3, PU_S1, PU_S2, PU_S3, RW_S1, RW_S2, RW_S3, attention, user_id)
                cursor.execute(stmt, args)
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"""Error occured while adding UES with values FA_S1={FA_S1}, 
                  FA_S2={FA_S2}, FA_S3={FA_S3}, PU_S1={PU_S1},
                PU_S2={PU_S2}, PU_S3=({PU_S3}, RW_S1=({RW_S1}, RW_S2={RW_S2}, RW_S3={RW_S3}, 
                attention_check={attention} for user {user_id}""")
    
    def add_cemi(self, pm_1, pm_2, pm_3, pm_4, pm_5, pm_6, pm_7, pm_8, pm_9, pm_10, pm_11, user_id):
        try: 
            with self.conn.cursor() as cursor:
                stmt = """UPDATE \"user\" SET PM_1=(%s), PM_2=(%s), PM_3=(%s),
                 PM_4=(%s), PM_5=(%s), PM_6=(%s), PM_7=(%s), PM_8=(%s), 
                 PM_9=(%s), PM_10=(%s), PM_11=(%s) WHERE user_id=(%s)"""
                args = (pm_1, pm_2, pm_3, pm_4, pm_5, pm_6, pm_7, pm_8, pm_9, pm_10, pm_11, user_id)
                cursor.execute(stmt, args)
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"""Error occured while adding CEMI with values PM_1={pm_1}, PM_2={pm_2}, 
                  PM_3={pm_3}, PM_4={pm_4}, PM_5={pm_5}, PM_6={pm_6}, PM_7={pm_7}, PM_8={pm_8}, 
                 PM_9={pm_9}, PM_10={pm_10}, PM_11={pm_11} for user {user_id}""")
            
    def add_last_page(self, cc1, cc2, cc3, cc4, pe1, pe2, pe3, education, job, anm, end_time, user_id):
        try:
            with self.conn.cursor() as cursor:
                stmt = """UPDATE \"user\" SET CC_1=(%s), CC_2=(%s), CC_3=(%s),
                        CC_4=(%s), PE_1=(%s), PE_2=(%s), PE_3=(%s), education=(%s),
                        job=(%s), general_remarks=(%s), end_time=(%s) WHERE user_id=(%s)"""
                args = (cc1, cc2, cc3, cc4, pe1, pe2, pe3, education, job, anm, end_time, user_id)
                cursor.execute(stmt, args)
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"""Error occured while adding final page with values CC_1={cc1}, 
                  CC_2={cc2}, CC_3={cc3}, CC_4={cc4}, PE_1={pe1}, PE_2={pe2}, PE_3={pe3}, 
                  education={education}, job={job}, general_remarks={anm}, end_time = {end_time} for user {user_id}""")
    

    def get_target_behaviour(self, chat_id):
        stmt = "SELECT target_behaviour from \"chat\" WHERE chat_id=(%s)"
        args = (chat_id, )
        
        cursor = self.conn.cursor()
        
        cursor.execute(stmt, args)
        target_behaviour = cursor.fetchone()
        cursor.close()
        #print(f"Target Behaviour for Chat {chat_id} is {target_behaviour[0]}")
        return target_behaviour[0]
        
        
    def add_chat(self, date, user_id, target_behaviour = "sein Verhalten ändern",  num_turns=0, change_talk_ratio = 0.0, top_utterance_type=None):
        current_chat_id = None
        try: 
            with self.conn.cursor() as cursor:
                stmt = """INSERT INTO "chat" (date, user_id, target_behaviour, num_turns, change_talk_ratio, top_utterance_type) 
                        VALUES (%s, %s, %s, %s, %s, %s)"""
                args = (date, user_id, target_behaviour, num_turns, change_talk_ratio, top_utterance_type)
                cursor.execute(stmt, args)
            self.conn.commit()
            #print(args)
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error occurred while adding chat for user {user_id}", e)

        cursor = self.conn.cursor()
        
        stmt = "SELECT lastval() FROM \"chat\""
        cursor.execute(stmt)
        current_chat_id = cursor.fetchone()[0]
        cursor.close()
        return current_chat_id
           
    def add_turn(self, turn_id, chat_id, user_utterance, datetime, bot_utterance=None, valence=None, valence_score = 0.0, label=None, label_score=0.0, sublabel=None, sublabel_score=0.0, bot_action=None, user_rating=None, user_rating_explanation=None, bot_datetime = None):
        turn_id += 1
        try:
            with self.conn.cursor() as cursor:
                stmt = """INSERT INTO "turn" (turn_id, chat_id, datetime, user_utterance, valence, 
                    valence_score, label, label_score, sublabel, sublabel_score, 
                    bot_action, bot_datetime, bot_utterance, user_rating, user_rating_explanation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                args = (turn_id, chat_id, datetime, user_utterance, valence, valence_score, label, label_score, sublabel, sublabel_score, bot_action, bot_datetime, bot_utterance, user_rating, user_rating_explanation)
                cursor.execute(stmt, args)
            self.conn.commit()
            #print(f"Turn {turn_id} to chat {chat_id} added!")
            return turn_id
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error occurred while adding turn {turn_id} with utterance {user_utterance} and bot_action {bot_action} to chat {chat_id}", e)
    
    def update_target_behaviour(self, choice, chat_id):
        try:
            with self.conn.cursor() as cursor:
                stmt = "UPDATE \"chat\" SET target_behaviour = (%s) WHERE chat_id = (%s)"
                args = (choice, chat_id)
                cursor.execute(stmt, args)
            self.conn.commit()
            print(f"Updated target behaviour to {choice} in chat {chat_id}")
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error occurred while updating target behaviour to {choice} in chat {chat_id}", e)
    
    '''def update_state(self, chat_id, new_state):
        try:
            with self.conn.cursor() as cursor:
                stmt = "UPDATE \"chat\" SET state = (%s) WHERE chat_id = (%s)"
                args = (new_state, chat_id)
                cursor.execute(stmt, args)
            self.conn.commit()
            print(f"Conversation state updated to {new_state}")
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error occurred while updating state to {new_state} in chat {chat_id}", e)'''
    
    def update_turn_rating(self, rating, turn_id, chat_id):
        try:
            with self.conn.cursor() as cursor:
                stmt = "UPDATE \"turn\" SET user_rating = (%s) WHERE turn_id = (%s) AND chat_id = (%s)"
                args = (rating, turn_id, chat_id)
                cursor.execute(stmt, args)
            self.conn.commit()
            #print(f"updated user rating of turn {turn_id} in  chat {chat_id} to {rating}")
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error occurred while updating user rating of turn {turn_id} in chat {chat_id} to {rating}", e)

    def update_turn_rating_explanation(self, rating_explanation, turn_id, chat_id):
        try:
            with self.conn.cursor() as cursor:
                stmt = "UPDATE \"turn\" SET user_rating_explanation = (%s) WHERE turn_id = (%s) AND chat_id = (%s)"
                args = (rating_explanation, turn_id, chat_id)
                cursor.execute(stmt, args)
            self.conn.commit()
            #print(f"added explanation to turn {turn_id} in chat {chat_id}")
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error occurred while adding explanation {rating_explanation} to turn {turn_id} in chat {chat_id}", e)

    def update_bot_turn(self, bot_turn, bot_datetime, turn_id, chat_id):
        try: 
            with self.conn.cursor() as cursor:
                stmt = "UPDATE \"turn\" SET bot_utterance = (%s), bot_datetime = (%s) WHERE turn_id = (%s) AND chat_id = (%s)"
                args = (bot_turn, bot_datetime, turn_id, chat_id)
                cursor.execute(stmt, args)
            self.conn.commit()
            #print(f"added bot utterance {bot_turn} to turn {turn_id} in chat {chat_id}")
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error occurred while adding bot utterance {bot_turn} to turn {turn_id} in chat {chat_id}", e)
    
    '''def delete_item(self, item_text):
        stmt = "DELETE FROM items WHERE description = (%s)"
        args = (item_text, )
        self.conn.execute(stmt, args)
        self.conn.commit()'''
        
    def check_user_exists(self, user_id):
        cursor = self.conn.cursor()
        stmt = "SELECT * FROM \"user\" WHERE user_id=(%s)"
        args = (user_id, )
        cursor.execute(stmt, args)
        #self.conn.commit()
        results = cursor.fetchone()
        cursor.close()
        if results == None:
            # print("User doesn't exist")
            return False
        else:
            # print(f"Database entry: {results}")
            return True
    
    def get_all_prev_turns_in_conv(self, chat_id):
        cursor = self.conn.cursor()
        stmt = "SELECT user_utterance from \"turn\" WHERE chat_id=(%s)"
        args = (chat_id, )
        cursor.execute(stmt, args)
        cursor.close()
        results = []
        for row in cursor.fetchall():
            #row)
            results.append({"role": "user", "content": row})
        return results
    
    '''def get_last_user_conv(self, user_id):
        cursor = self.conn.cursor()
        stmt = """SELECT chat_id FROM \"chat\" WHERE user_id=(%s)
                ORDER BY chat_id DESC LIMIT 1"""
        args = (user_id, )
        print(args)
        cursor.execute(stmt, args)
        results = cursor.fetchone()
        cursor.close()
        if results == None:
            print("No existing chat for user!")
        else:
            print(f"Last available Chat ID for user: {results[0]}")
            return results[0]'''
    
    def get_prev_target_behaviour(self, chat_id, user_id):
        cursor = self.conn.cursor()
        stmt = "SELECT target_behaviour FROM \"chat\" WHERE chat_id=(%s) AND user_id=(%s)"
        args = (chat_id, user_id)
        cursor.execute(stmt, args)
        results = cursor.fetchall()
        cursor.close()
        #print(results)
        return results[0][0]
    
    def get_condition(self):
        cursor = self.conn.cursor()
        stmt = "SELECT condition FROM \"user\""
        cursor.execute(stmt)
        results = cursor.fetchall()
        cursor.close()
        #print(results)
        if len(results) == 0:
            return "framework"
        else:
            condition_count = Counter(elem[0] for elem in results if elem[0] != None)
            #print(condition_count)
            most_tested = max(condition_count, key=condition_count.get)
            #print(most_tested)
            if most_tested == "framework":
                return "no_system"
            else:
                return "framework"
        #return "framework"
        
    def get_existing_condition(self, user_id):
        cursor = self.conn.cursor()
        stmt = "SELECT condition FROM \"user\" WHERE user_id=(%s)"
        args = (user_id,)
        cursor.execute(stmt, args)
        results = cursor.fetchone()
        cursor.close()
        return results[0]

    
    def get_prev_bot_actions(self, chat_id):
        cursor = self.conn.cursor()
        stmt = "SELECT bot_action FROM \"turn\" WHERE chat_id=(%s)"
        args = (chat_id,)
        cursor.execute(stmt, args)
        results = cursor.fetchall()
        cursor.close()
        counted_behaviours = Counter(elem[0] for elem in results if elem[0] != None)
        #print(f"Previous bot behaviours: \n{counted_behaviours}")
        return counted_behaviours
    
    def build_context_window(self, chat_id, num_turns):
        cursor = self.conn.cursor()
        bot_stmt = "SELECT bot_utterance FROM \"turn\" WHERE chat_id=(%s) ORDER BY turn_id DESC"
        user_stmt = "SELECT user_utterance FROM \"turn\" WHERE chat_id=(%s) ORDER BY turn_id DESC"
        args = (chat_id, )
        cursor.execute(bot_stmt, args)
        bot_results = cursor.fetchall()
        cursor.execute(user_stmt, args)
        user_results = cursor.fetchall()
        cursor.close()
        
        context_window_array = [] #"{\"role\": \"user\", \"content\":\""
        
        for i in reversed(range(0, num_turns)):
            #print(user_results[i][0])
            #print(bot_results[i][0])
            user_utt = {"role": "user", "content": user_results[i][0]}
            context_window_array.append(user_utt)
            if bot_results[i][0] != None:
                bot_utt = {"role": "assistant", "content": bot_results[i][0]}
                context_window_array.append(bot_utt)
            #context_window_string += user_results[i][0] + "\"},{\"role\": \"assistant\", \"content\":\"" + bot_results[i][0] + "\"}, {\"role\": \"user\", \"content\":\""
        #context_window_string += user_utterance + "\"}"
        #current_user_utt = {"role": "user", "content": user_results[len(user_results)][0]}
        # context_window_array.append(current_user_utt)
        #print(f"This is the part of the conversation we will pass to GPT-4: \n {context_window_array}")
        return context_window_array