from functions import *
import psycopg2
import random
import time
import datetime

class ConversationHandler():
    def __init__(self, db):
          self.db = db
          
    def start_conv(self, prolific_id, chat_id, turn_id, conv_state, readiness_to_change_start):
        print(readiness_to_change_start)
        if readiness_to_change_start == None:
            return hide_chtbt, chat_id, turn_id, prolific_id, conv_state, show_block_part, show_mrkdwn
        else:
            try:
                with self.db.conn:
                    self.db.add_scale_item(prolific_id, "readiness_to_change_start", int(readiness_to_change_start))
                    chat_id = self.db.add_chat(datetime.datetime.now(), prolific_id)
                    #print(chat_id)
                    turn_id = self.db.add_turn(turn_id=turn_id, chat_id=chat_id, user_utterance="start", datetime=datetime.datetime.now())
                    #print(turn_id)
            except psycopg2.Error as e:
                print(f"Transaction error occured: {e}, USER: {prolific_id}, CHAT: {chat_id}, TURN: {turn_id}")
            print(f"Chat {chat_id} started with user_id {prolific_id}")
            conv_state = "New"
            return (show_chtbt, chat_id, turn_id, prolific_id, conv_state, hide_block_part, hide_mrkdwn) 

    def greet(self, history, chat_id, turn_id):
        bot_message = """Hi, I'm MIcha, your motivational chatbot. 
                            My goal is to help you reflect on your behaviour and support you in developing a plan for behaviour change. 
                            Please think about my questions carefully and see them mainly as food for thought that will bring you mentally closer to your goal. 
                            I am not here to give you tips or recommendations for action, but to help you become clear about your motivations and values. 
                                
                            What behaviour change do you want to talk about today?"""
        try:
            with self.db.conn:
                self.db.update_bot_turn(bot_message, datetime.datetime.now(), turn_id, chat_id)
        except psycopg2.Error as e:
                print(f"Transaction error occured: {e}, CHAT: {chat_id}, TURN: {turn_id}, BOT_MESSAGE: {bot_message}")
        history = [["Hi",""]]
        for character in bot_message:
            history[0][1] += character
            time.sleep(0.02)
            yield history
        #history[0][1] += bot_message
        #yield history

    def enable_dropdown(self, chatbot, readiness):
        if readiness == -1:
            return hide_drpdwn
        else:
            return show_drpdwn

    def set_topic(self, topic_choice, history, chat_id, turn_id):
            #print(topic_choice)
            #print(history)
            mapping = {"Ich möchte nachhaltiger leben": "nachhaltiger leben", 
                        "Ich möchte weniger prokrastinieren": "weniger prokrastinieren",
                        "I would like to eat healthier": "gesünder essen"}
            topic = mapping[topic_choice]
            try:
                with self.db.conn:
                    self.db.update_target_behaviour(topic, chat_id)
                    turn_id = self.db.add_turn(turn_id, chat_id, topic_choice, datetime=datetime.datetime.now())
            except psycopg2.Error as e:
                print(f"Transaction error occured: {e}, CHAT: {chat_id}, TOPIC: {topic_choice}, TURN: {turn_id} ")
            return (history + [[topic_choice, None]], topic, turn_id, hide_drpdwn, show_txtbx)
        
    def ask_next(self, topic, history, chat_id, turn_id):
        bot_message = f"So you want to eat healthier. Can you tell me something about why this change is important to you?"
        #print("History: ", history)
        try:
            with self.db.conn:
                self.db.update_bot_turn(bot_message, datetime.datetime.now(), turn_id, chat_id)
        except psycopg2.Error as e:
                print(f"Transaction error occured: {e}, CHAT: {chat_id}, TURN: {turn_id}, BOT_MESSAGE: {bot_message}", e)
        history[-1][1] = ""
        for character in bot_message:
            history[-1][1] += character
            time.sleep(0.02)
            yield history

    def disable_buttons(self, button, turn_id, chat_id):
        rating = str.split(button, sep=" ")[5]
        #print(rating)
        try:
            with self.db.conn:
                self.db.update_turn_rating(rating, turn_id, chat_id)
        except psycopg2.Error as e:
            print(f"Transaction error occured: {e}, CHAT: {chat_id}, TURN: {turn_id}, RATING: {rating}")
        return (hide_block_part, show_txtbx, hide_mrkdwn)

    def get_initial_text_input(self, user_message, chat_id, turn_id, history):
        try:
            with self.db.conn:
                turn_id = self.db.add_turn(turn_id=turn_id, chat_id=chat_id, user_utterance=user_message, datetime=datetime.datetime.now())
        except psycopg2.Error as e:
            print(f"Transaction error occured: {e}, CHAT: {chat_id}, TURN: {turn_id}, USER_MESSAGE: {user_message}")
        #print(f"Turn id: {turn_id}")
        return (turn_id, history + [[user_message, None]], "")

    def trigger_likert(self, user_message):
            return(hide_txtbx, show_lkrt)
        
    def ask_likert_q(self, history, chat_id, turn_id):
        '''bot_message = random.choice(["Wie wichtig ist dir diese Veränderung auf einer Skala von 0 (überhaupt nicht) bis 10 (sehr)",
                    "Wie zuversichtlich bist du auf einer Skala von 0 (überhaupt nicht) bis 10 (sehr), dass du diese Veränderung durchführen kannst?",
                    "Auf einer Skala von 0 (überhaupt nicht) bis 10 (sehr), wie interessiert bist du jetzt gerade daran, diese Veränderung durchzuführen?", 
                    "Wie bereit bist du auf einer Skala von 0 (überhaupt nicht) bis 10 (sehr) diese Veränderung durchzuführen?"])'''
        bot_message = "On a scale from 0 (not at all) to 10 (very much), how important is this change to you?"
        try:
            with self.db.conn:
                self.db.update_bot_turn(bot_message, datetime.datetime.now(), turn_id, chat_id)
        except psycopg2.Error as e:
            print(f"Transaction error occured: {e}, CHAT: {chat_id}, TURN: {turn_id}, BOT_MESSAGE: {bot_message}")
        history[-1][1] = ""
        for character in bot_message:
            history[-1][1] += character
            time.sleep(0.02)
            yield history

    def save_likert(self, likert, turn_id, chat_id, history, conv_state):
        likert_reply = str(likert)
        try:
            with self.db.conn:
                turn_id = self.db.add_turn(turn_id, chat_id, likert_reply, datetime=datetime.datetime.now())
        except psycopg2.Error as e:
                print(f"Transaction error occured: {e}, CHAT: {chat_id}, TURN: {turn_id}, RESPONSE: {likert_reply}")
        conv_state = "Main"
        return (hide_lkrt, turn_id, show_txtbx, history + [[likert_reply, None]], conv_state)

    def ask_explanation(self, likert_reply, history, turn_id, chat_id):
        bot_message = ""
        if likert_reply == 0:
            bot_message = f"Eine {likert_reply}. Das klingt als stündest du dieser Veränderung überhaupt nicht zuversichtlich gegenüber. Erzähl mir bitte mehr über deine Einstellung. Warum hast du nicht {likert_reply+1} oder mehr angegeben?"
        elif likert_reply == 10:
            bot_message = f"Eine {likert_reply}. Das klingt als stündest du dieser Veränderung sehr zuversichtlich gegenüber. Erzähl mir bitte mehr über deine Einstellung. Warum hast du nicht {likert_reply-1} oder weniger angegeben?"
        elif likert_reply > 5:
            bot_message = f"A {likert_reply}. So you have an overall positive attitude towards this change. Can you tell me a bit more about this assessment? Why didn't you give a higher or lower value?"
        else:
            bot_message = f"Eine {likert_reply}. Das klingt als stündest du dieser Veränderung nicht allzu zuversichtlich gegenüber. Erzähl mir bitte mehr über deine Einstellung. Warum hast du keinen höheren oder niedrigeren Wert angegeben?"
        try:
            with self.db.conn:
                self.db.update_bot_turn(bot_message, datetime.datetime.now(), turn_id, chat_id)
        except psycopg2.Error as e:
                print(f"Transaction error occured: {e}, CHAT: {chat_id}, TURN: {turn_id}, BOT_MESSAGE: {bot_message}")
        history[-1][1] = ""
        for character in bot_message:
            history[-1][1] += character
            time.sleep(0.02)
            yield history

    def add_rating_explanation(self, explanation, turn_id, chat_id):
        if explanation != '':
            try:
                with self.db.conn:
                    self.db.update_turn_rating_explanation(explanation, turn_id, chat_id)
            except psycopg2.Error as e:
                print(f"Transaction error occured: {e}, CHAT: {chat_id}, TURN: {turn_id}, RATING_EXPLANATION: {explanation}")
        return hide_txtbx, "", enable_txtbx, show_txtbx

    def disable_text(self, textbox):
            return disable_txtbx

    def user(self, user_message, history, turn_id, chat_id, previous_turn_type, conv_state, condition):
        #condition = self.db.get_condition(user_id)
        #print(f"CONDITION: {condition}")
        
        most_used_behaviour = ""
        action = None
        description = None
        classifications = get_utterance_classifications(user_message)
        #print(classifications)
        # add classification here + add valence, label and sublabel to self.db. return all classifications and pass to bot
        #print(f"Turn id: {turn_id}")

        if turn_id < 9: #creates turn 9
            conv_state = "Main"
            if condition == "framework":
                previous_behaviours = self.db.get_prev_bot_actions(chat_id)
                #print(previous_behaviours)
                try:
                    most_used_behaviour = max(previous_behaviours, key=previous_behaviours.get)
                except: 
                    most_used_behaviour = "No saved behaviours"
                #print(f"MOST USED BEHAVIOUR: {most_used_behaviour}")
                action, description = get_appropriate_action(classifications["valence"], classifications["label"], 
                                        most_used_behaviour, previous_turn_type, classifications["sublabel"])
                #print(action)
                #print(f"CHOSEN ACTION: {action}")
        elif turn_id == 9: #creates turn 10
            conv_state = "Summary"
            action = "Summary"
        elif turn_id == 10: #creates turn 11
            conv_state = "Next Steps"
            action = "Next Steps"
        elif turn_id == 11: #creates turn 12
            conv_state = "Goodbye"
            action = "Goodbye"
        
        try:
            with self.db.conn:
                turn_id = self.db.add_turn(turn_id=turn_id, chat_id=chat_id, user_utterance=user_message, datetime = datetime.datetime.now(), 
                                        valence=classifications["valence"], valence_score=classifications["valence_score"],
                                        label=classifications["label"], label_score=classifications["label_score"],
                                        sublabel=classifications["sublabel"], sublabel_score=classifications["sublabel_score"],
                                        bot_action=action)
        except psycopg2.Error as e:
                print(f"Transaction error occured: {e}, CHAT: {chat_id}, TURN: {turn_id}, USER_UTTERANCE: {user_message}, BOT_ACTION: {action}")
        #print(f"Conversation State {conv_state}")
            # msg, chatbot, turn_id, appropriate_action, action_description, previous_turn_type
        return ("", hide_txtbx, history + [[user_message, None]], turn_id, action, description, previous_turn_type, conv_state)

    def bot(self, user_utterance, history, turn_id, chat_id, topic, action, description, conv_state, condition):
        context = self.db.build_context_window(chat_id, turn_id)
        #print(topic)
        #print(action)
        #print(description)
        bot_message = ""
        if conv_state == "Main":
            if condition == "framework":
                bot_message = get_bot_message(context, topic, action, description)
            elif condition == "vanilla":
                bot_message = get_vanilla_message(context, topic)
            elif condition == "no_system":
                bot_message = get_no_system_prompt_message(context)
        elif conv_state == "Summary":
            bot_message = get_summary(context)
        elif conv_state == "Next Steps":
            bot_message = """Verstanden! Bitte verrate mir abschließend nochmal was dein nächster Schritt konkret sein wird."""
        elif conv_state == "Goodbye":
            bot_message = """Vielen Dank für deine Offenheit in unserem Gespräch. 
                            Ich hoffe es hat dir dabei geholfen, deinem Ziel zumindest gedanklich etwas näher zu kommen."""
        try:
            with self.db.conn:
                self.db.update_bot_turn(bot_message, datetime.datetime.now(), turn_id, chat_id)
        except psycopg2.Error as e:
                print(f"Transaction error occured: {e}, CHAT: {chat_id}, TURN: {turn_id}, BOT_MESSAGE: {bot_message}")
        history[-1][1] = ""
        for character in bot_message:
            history[-1][1] += character
            time.sleep(0.05)
            yield history

    def show_buttons(self, conv_state, button_row):
            if conv_state != "Goodbye":
                return show_mrkdwn, show_block_part
            else:
                return hide_mrkdwn, hide_block_part
            
    def check_conv_end(self, conv_state):
        if conv_state=="Goodbye":
            return show_btn
        else:
            return hide_btn
