from functions import *
import psycopg2
from dbelper import DBHelper
from conversation_handler import *

with open('resources/Work_Task_Situations.md', 'r') as file:
    situations_descriptions = file.read()

with open('resources/informed_consent.md', 'r') as file:
    informed_consent_text = file.read()

with open('resources/final_paeg.md', 'r') as file:
    final_page_text = file.read()

with gr.Blocks(css="custom.css") as demo:

    db = DBHelper()
    ch = ConversationHandler(db)

    with gr.Column(visible=True) as informed_consent:
        consent_info = gr.Markdown(value=informed_consent_text, visible=True)
        prolific_id = gr.Textbox(label="Bitte Geben Sie ihre Prolific ID ein:", interactive=True)
        consent_given = gr.Checkbox(label="Ich habe die oben dargelegten Informationen gelesen und verstanden.")

    # Initial Information
    """with gr.Column(visible=False) as pre_test:
        info = gr.Markdown(value="### Bitte beantworten Sie zunächst ein paar Fragen zu Ihrer Person. Diese sind anonym und können nicht genutzt werden, um auf Sie zurückzuführen.")
        with gr.Row() as demographics:
            education = gr.Dropdown(label="Was ist ihr höchster Schul- oder Hochschulabschluss?", 
                                    choices=["Hauptschulabschluss",
                                            "mittlere Reife",
                                            "abgeschlossene Berufsausbildung",
                                            "Abitur",
                                            "Bachelor-Abschluss",
                                            "Master-Abschluss",
                                            "Doktor-Grad"], visible=True)
            education_name = gr.HTML("education", visible=False)
        job = gr.Textbox(label="Was ist ihre aktuelle Haupttätigkeit?", visible=True)
        job_name = gr.HTML("job", visible=False)"""

    with gr.Column(visible=False) as situation_information:
        with gr.Box():
            situations = gr.Markdown(value=situations_descriptions, visible=True)
        with gr.Box():
            #contemplation_ladder_info = gr.Markdown("### Jede Sprosse auf dieser Leiter steht für den Stand der Überlegungen verschiedener Personen in Bezug auf die Verhaltensänderung in dem von Ihnen gewählten Szenario.")
            contemplation_ladder = gr.Image("contemplation_ladder.png").style(height=400)
            #contemplation_ladder_task = gr.Markdown("### Geben Sie die Zahl an, bei der Sie sich jetzt befinden")
            readiness_to_change_start = gr.Slider(label="Ich bin bei Sprosse...", minimum=0, maximum=10, step=1)
            readiness_to_change_start_state = gr.State()
        to_conv = gr.Button("Weiter")
        # to_post_test = gr.Button("Weiter zum Debuggen", visible=True) ## beim debuggen to_post_test variable unten auskommentieren

    # Main part
    chatbot = gr.Chatbot(visible=False)
    likert = gr.Slider(maximum=10, step=1, visible=False)
    reason_for_change = gr.Textbox(visible=False)
    msg = gr.Textbox(label="Deine Antwort", visible=False, interactive=True)
    explanation = gr.Textbox(label="Explain your rating", 
                             info="If you don't want to give an explanation, press Enter.", 
                             visible=False, elem_id="explanation")
    topic_choice = gr.Dropdown(["Ich möchte nachhaltiger leben", 
                                "Ich möchte weniger prokrastinieren",
                                "I would like to eat healthier"], visible=False, interactive=True)
    button_text = gr.Markdown("Rate my last reply:", visible=False, elem_id="explanation")
    with gr.Row(visible=False) as button_row:
        upvote_btn = gr.Button(value="👍  The answer is good/helpful", interactive=True, visible=True)
        downvote_btn = gr.Button(value="👎  The answer is bad/inappropriate", interactive=True, visible=True)
        flag_btn = gr.Button(value="⚠️  The answer is insulting/hurtful", interactive=True, visible=True)
    to_post_test = gr.Button("Next", visible=False)

    # create all needed states - these will be tracked for users independently
    chat_id = gr.State()
    user_id = gr.State()
    previous_turn_type = gr.State()
    appropriate_action = gr.State()
    action_description = gr.State()
    topic = gr.State()
    turn_id = gr.State(value=0)
    conv_state = gr.State()
    condition = gr.State(value="framework")
    pretest_fulfilled = gr.State(value = False)

    # Post-test (get demographic information, usability & therapeutic alignment)
    def make_ues(label):
        return gr.Radio(label=label, choices=["Stimme überhaupt nicht zu",
                                     "Stimme eher nicht zu",
                                     "Stimme weder zu noch ab",
                                     "Stimme eher zu",
                                     "Stimme voll und ganz zu"])
    def make_ta(label):
        return gr.Radio(label=label, choices=["selten",
                                     "manchmal",
                                     "öfters",
                                     "sehr oft",
                                     "immer"])
    
    def make_cemi(label):
        return gr.Radio(label=label, choices=["überhaupt nicht",
                                              "ein wenig",
                                              "manchmal",
                                              "sehr viel",
                                              "immer"])
    
    with gr.Box(visible=False) as post_test:
        post_study = gr.Markdown("""### Bitte beantworten Sie im Folgenden noch ein paar Fragen zu Ihrer Unterhaltung mit MIcha.""", visible=True)
        identification = gr.Slider(label="Auf einer Skala von 0 bis 10, wie sehr konnten Sie sich mit der von Ihnen gewählten Situation identifizieren?",
                                maximum=10, step=1, visible=True)
        identification_state = gr.State()
        change_pref = gr.Slider(label="Auf einer Skala von 0 bis 10, wie sehr versuchen Sie aktuell, die von Ihnen gewählte Verhaltensänderung in Ihrem Alltag umzusetzen?",
                                maximum=10, step=1, visible=True)
        change_pref_state = gr.State()
        #contemplation_ladder_info = gr.Markdown("Jede Sprosse auf dieser Leiter steht für den Stand der Überlegungen verschiedener Personen in Bezug auf die Verhaltensänderung in dem von Ihnen gewählten Szenario.")
        contemplation_ladder = gr.Image("contemplation_ladder.png").style(height=400)
        #contemplation_ladder_task = gr.Markdown("Geben Sie die Zahl an, bei der Sie sich jetzt befinden")
        readiness_to_change_end = gr.Slider(label="Ich bin bei Sprosse...", minimum=0, maximum=10, step=1)
        readiness_to_change_end_state = gr.State()
        to_ta = gr.Button("Weiter")

        # https://www.researchgate.net/profile/Juergen-Barth-2/publication/228336420_Die_deutschsprachige_Version_des_Working_Alliance_Inventory_-_short_revised_WAI-SR_-_Ein_schulenubergreifendes_okonomisches_und_empirisch_validiertes_Instrument_zur_Erfassung_der_therapeutischen_Allia/links/0912f502529add3220000000/Die-deutschsprachige-Version-des-Working-Alliance-Inventory-short-revised-WAI-SR-Ein-schulenuebergreifendes-oekonomisches-und-empirisch-validiertes-Instrument-zur-Erfassung-der-therapeutischen-Al.pdf
    with gr.Box(visible=False) as therapeutic_alignment:
        ta_text = gr.Markdown("""### Bitte geben Sie an, zu welchem Grad Sie mit jeder der folgenden Aussagen übereinstimmen.""", visible=True)
        ta1 = make_ta("Durch das Gespräch ist mir klarer geworden, wie ich mich verändern kann.") # adapted
        ta1_state = gr.State()
        ta2 = make_ta("Das Gespräch eröffnete mir neue Sichtweisen auf mein Problem.") #adapted
        ta2_state = gr.State()
        ta3 = make_ta("Ich glaube MIcha mag mich.")
        ta3_state = gr.State()
        ta4 = make_ta("MIcha und ich arbeiten gemeinsam daran, Ziele zu setzen.") # adapted
        ta4_state = gr.State()
        ta5 = make_ta("MIcha und ich achten einander.")
        ta5_state = gr.State()
        ta6 = make_ta("MIcha und ich arbeiten auf Ziele hin, über die wir uns einig sind.")
        ta6_state = gr.State()
        ta7 = make_ta("Ich spüre, dass MIcha mich schätzt.")
        ta7_state = gr.State()
        ta8 = make_ta("MIcha und ich stimmen überein, woran es für mich wichtig ist zu arbeiten")
        ta8_state = gr.State()
        ta9 = make_ta("Ich spüre, dass MIcha auch dann zu mir steht, wenn ich etwas tue, was er nicht gutheißt.")
        ta9_state = gr.State()
        ta10 = make_ta("Ich spüre, dass das, was ich im Gespräch besprochen habe, mir helfen wird, die von mir gewünschten Veränderungen zu erreichen.") #adapted
        ta10_state = gr.State()
        ta11 = make_ta("MIcha und ich sind uns im Klaren darüber, welche Veränderungen gut für mich wären.")
        ta11_state = gr.State()
        ta12 = make_ta("Ich glaube, dass es richtig ist, wie wir an meinem Problem arbeiten.")
        ta12_state = gr.State()
        to_engagement = gr.Button("Weiter")

    with gr.Box(visible=False) as user_engagement:
        ta_text = gr.Markdown("""### Hier sehen Sie einige Aussagen über Ihrer Erfahrung bei der Nutzung von MIcha. 
                              ### Bitte geben Sie an, zu welchem Grad Sie mit jeder der Aussagen übereinstimmen.""", visible=True)
        FA_S1 = make_ues("Ich habe mich bei der Anwendung von MIcha vergessen.") #adapted
        fa_s1_state = gr.State()
        FA_S2 = make_ues("Die Zeit verging wie im Flug, als ich MIcha anwendete.")
        fa_s2_state = gr.State()
        FA_S3 = make_ues("Ich war gänzlich in die Anwendung vertieft.")
        fa_s3_state = gr.State()
        PU_S1 = make_ues("Ich war frustriert, während ich MIcha nutzte.")
        pu_s1_state = gr.State()
        PU_S2 = make_ues("Ich fand die Anwendung von MIcha verwirrend.")
        pu_s2_state = gr.State()
        attention = make_ues("Wählen Sie die Antwortmöglichkeit ganz links aus.")
        attention_state = gr.State()
        PU_S3 = make_ues("Die Benutzung von MIcha war anstrengend.")
        pu_s3_state = gr.State()
        RW_S1 = make_ues("Die Nutzung von MIcha war lohnenswert.") # adapted
        rw_s1_state = gr.State()
        RW_S2 = make_ues("Meine Erfahrung mit MIcha hat sich gelohnt.")
        rw_s2_state = gr.State()
        RW_S3 = make_ues("Diese Erfahrung hat mich interessiert.") # selbst übersetzt
        rw_s3_state = gr.State()
        # Add Aesthetic appeal? -> HE et al haben aesthetic appeal auch weggelassen
        to_perception = gr.Button("Weiter")

            
    with gr.Box(visible=False) as perception_mi:
       pm_text = gr.Markdown("""### In den folgenden Fragen geht es darum, wie MIcha mit Ihnen über die gewählte Verhaltensänderung kommuniziert hat.
       ### Bitte geben Sie an, zu welchem Grad Sie mit jeder der Aussagen übereinstimmen.
                             """)
       pm_start_text = gr.Markdown("**Während dem Gespräch hat MIcha...**")
       pm_1 = make_cemi("Ihnen geholfen, über eine Änderung Ihres Verhaltens zu sprechen.")
       pm_1_state = gr.State()
       pm_2 = make_cemi("Sie dazu gebracht, über etwas zu sprechen, das Sie nicht besprechen wollten.")
       pm_2_state = gr.State()
       pm_3 = make_cemi("Ihnen geholfen, über die Notwendigkeit einer Verhaltensänderung zu sprechen.")
       pm_3_state = gr.State()
       pm_4 = make_cemi("Ihnen geholfen, die  Vor- und Nachteile einer Verhaltensänderung zu erwägen.")
       pm_4_state = gr.State()
       pm_5 = make_cemi("Mit Ihnen argumentiert, um Ihr Verhalten zu ändern")
       pm_5_state = gr.State()
       pm_6 = make_cemi("Ihnen geholfen, hoffnungsvoll zu sein, was die Veränderung Ihres Verhaltens betrifft")
       pm_6_state = gr.State()
       pm_7 = make_cemi("Als Partner bei Ihrer Verhaltensänderung agiert.")
       pm_7_state = gr.State()
       pm_8 = make_cemi("Ihnen geholfen, zu erkennen, dass Sie Ihr Verhalten ändern müssen.")
       pm_8_state = gr.State()
       pm_9 = make_cemi("Ihnen gesagt, was Sie tun sollen.")
       pm_9_state = gr.State()
       pm_10 = make_cemi("Ihnen geholfen, sich in Ihrer Fähigkeit, Ihr Verhalten zu ändern, sicher zu fühlen.")
       pm_10_state = gr.State()
       pm_11 = make_cemi("Wie eine Autorität in Ihrem Leben agiert") 
       pm_11_state = gr.State()
       to_competence = gr.Button("Weiter")

    with gr.Column(visible=False) as comp_emp_pilot:   
        comp_emp_text = gr.Markdown("""### In den folgenden Fragen geht es um MIcha's Kompetenz und Empathiefähigkeit im Laufe des Gesprächs.""")
        with gr.Box(visible=True) as chatbot_competence:
            cc1 = make_ues("MIcha hat angemessen kommuniziert.")
            cc1_state = gr.State()
            cc2 = make_ues("MIcha hat richtig kommuniziert.")
            cc2_state = gr.State()
            cc3 = make_ues("MIcha wirkte kompetent.")
            cc3_state = gr.State()
            cc4 = make_ues("MIcha wirkte glaubwürdig.")
            cc4_state = gr.State()
        
        with gr.Box(visible=True) as perceived_empathy:
            pe1 = make_ues("MIcha scheint zu wissen, wie ich mich fühle.")
            pe1_state = gr.State()
            pe2 = make_ues("MIcha scheint mich zu verstehen.")
            pe2_state = gr.State()
            pe3 = make_ues("MIcha versetzt sich in meine Lage.")
            pe3_state = gr.State()

        with gr.Box(visible=True) as pilot_qs:
            pilot_qs_text = gr.Markdown("""### Zuletzt beantworten Sie bitte noch ein paar Fragen zu Ihrer Person. Diese sind anonym und können nicht genutzt werden, um auf Sie zurückzuführen.""")
            education = gr.Dropdown(label="Was ist ihr höchster Schul- oder Hochschulabschluss?", 
                                    choices=["Hauptschulabschluss",
                                            "mittlere Reife",
                                            "abgeschlossene Berufsausbildung",
                                            "Abitur",
                                            "Bachelor-Abschluss",
                                            "Master-Abschluss",
                                            "Doktor-Grad"], visible=True)
            education_state = gr.State()
            job = gr.Textbox(label="Was ist ihre aktuelle Haupttätigkeit?", visible=True)
            job_state = gr.State()
            anm = gr.Textbox(label="Haben Sie noch weitere Anmerkungen?")     
            anm_state = gr.State()
        to_final_page = gr.Button("Weiter")

    ausgefuellt = gr.Markdown("Bitte füllen Sie alle Felder aus.", visible=False, elem_id="explanation")
    ausgefuellt_likert = gr.Markdown("Bitte geben Sie bei allen Skalen eine Zahl zwischen 0 und 10 an.", visible=False, elem_id="explanation")


    with gr.Box(visible=False) as final_page:
        goodbye = gr.Markdown(value=final_page_text)

    def initial_info(consent, prolific_id):
        if prolific_id == "":
            condition = ""
            return show_block_part, hide_block_part, show_mrkdwn, False, prolific_id, condition
        elif db.check_user_exists(prolific_id):
            condition = db.get_existing_condition(prolific_id)
            print(condition)
            return hide_block_part, show_block_part, hide_mrkdwn, True, prolific_id, condition
        else: 
            condition = db.get_condition()
            print(condition)
            try:
                with db.conn:
                    db.add_user(user_id=prolific_id, condition=condition, start_time=datetime.datetime.now())
            except psycopg2.Error as e:
                print(f"Transaction error occured: {e}, adding USER {prolific_id}, CONDITION: {condition}", e)
        return hide_block_part, show_block_part, hide_mrkdwn, True, prolific_id, condition

    def update_state(user_tag, state, response):
        state = response
        return state
    
    def move_to_post_test(to_post_test):
        return hide_chtbt, hide_btn, show_block_part
    
    def check_ta(ta1, ta2, ta3, ta4, ta5, ta6, ta7, ta8, ta9,
                ta10, ta11, ta12, user_id):
        all_present = True
        ta_list = [ta1, ta2, ta3, ta4, ta5, ta6, ta7, ta8, ta9, ta10, ta11, ta12]
        for key in ta_list:
            # print(key)
            #db.add_scale_item(user_id, ta_dict[key], key)
            if key == None:
                all_present = False
        
        if all_present == False:
            return show_mrkdwn, hide_block_part, show_block_part
        else:
            try:
                with db.conn:
                    db.add_ta(ta1, ta2, ta3, ta4, ta5, ta6, ta7, ta8, ta9, ta10, ta11, ta12, user_id)
            except psycopg2.Error as e:
                print(f"""Transaction error occured: {e}, adding ta1 = {ta1}, ta2 = {ta2}, ta3 = {ta3}, 
                      ta4 = {ta4}, ta5 = {ta5}, ta6 = {ta6}, ta7 = {ta7}, ta8 = {ta8}, 
                       ta9 = {ta9}, ta10 = {ta10}, ta11 = {ta11}, ta12 = {ta12} to user {user_id}""")
            return hide_mrkdwn, show_block_part, hide_block_part
        
    def check_ues(FA_S1, FA_S2, FA_S3, PU_S1, PU_S2, PU_S3, RW_S1, RW_S2, RW_S3, attention, user_id):
        all_present = True
        ues_list = [FA_S1, FA_S2, FA_S3, PU_S1, PU_S2, PU_S3, RW_S1, RW_S2, RW_S3, attention]
        for key in ues_list:
            #print(key)
            #db.add_scale_item(user_id, ues_dict[key], key)
            if key == None: 
                all_present = False
        if all_present == False:
            return show_mrkdwn, hide_block_part, show_block_part
        else:
            try:
                with db.conn:
                    db.add_ues(FA_S1, FA_S2, FA_S3, PU_S1, PU_S2, PU_S3, RW_S1, RW_S2, RW_S3, attention, user_id)
            except psycopg2.Error as e:
                print(f"""Transaction error occured: {e}, adding UES with values fa1 = {FA_S1}, fa2 = {FA_S2}, fa3 = {FA_S3}, 
                      pu1 = {PU_S1}, pu2 = {PU_S2}, pu3 = {PU_S3}, rw1 = {RW_S1}, rw2 = {RW_S2}, 
                      rw3 = {RW_S3}, attention check = {attention} to user {user_id}""")
            return hide_mrkdwn, show_block_part, hide_block_part
        
    def check_mi(pm_1, pm_2, pm_3, pm_4, pm_5, pm_6,
                pm_7, pm_8, pm_9, pm_10, pm_11, user_id):
        all_present = True
        mi_list = [pm_1, pm_2, pm_3, pm_4, pm_5, pm_6,
                pm_7, pm_8, pm_9, pm_10, pm_11]
        #print(mi_dict)
        for key in mi_list:
            #print(key)
            #db.add_scale_item(user_id, mi_dict[key], key)
            if key == None: 
                all_present = False
        if all_present == False:
            return show_mrkdwn, hide_block_part, show_block_part
        else:
            try:
                with db.conn:
                    db.add_cemi(pm_1, pm_2, pm_3, pm_4, pm_5, pm_6, pm_7, pm_8, pm_9, pm_10, pm_11, user_id)
            except psycopg2.Error as e:
                print(f"""Transaction error occured: {e}, adding CEMI with values pm1 = {pm_1}, pm2 = {pm_2}, pm3 = {pm_3}, 
                      pm4 = {pm_4}, pm5 = {pm_5}, pm6 = {pm_6}, pm7 = {pm_7}, pm8 = {pm_8}, 
                      pm9 = {pm_9}, pm10 = {pm_10}, pm11 = {pm_11} to user {user_id}""")
            return hide_mrkdwn, show_block_part, hide_block_part
        
    def check_post_test(identification, change_pref, readiness, user_id):
        check_list = [identification, change_pref, readiness]
        all_present = True
        for key in check_list:
           # db.add_scale_item(user_id, check_dict[key], key)
            if key == None:
                all_present = False
        
        if all_present == False:
            return show_mrkdwn, hide_block_part, show_block_part
        else:
            db.add_post_test(int(identification), int(change_pref), int(readiness), user_id)
            return hide_mrkdwn, show_block_part, hide_block_part
        
    def check_comp_emp_pilot(user_id, cc1, cc2, cc3, cc4, pe1, pe2, pe3, education, job_state, job, anm):
        check_list = [cc1, cc2, cc3, cc4, pe1, pe2, pe3, education, job_state]
        
        all_present = True
        for key in check_list:
            if key == None:
                all_present = False
        
        if all_present == False:
            return show_mrkdwn, hide_block_part, show_block_part
        else:
            try: 
                with db.conn:
                    db.add_last_page(cc1, cc2, cc3, cc4, pe1, pe2, pe3, education, job, anm, datetime.datetime.now(), user_id)
            except psycopg2.Error as e:
                print(f"""Transaction error occured: {e}, adding CC, PE and demographics with values cc1 = {cc1}, 
                      cc2 = {cc2}, cc3 = {cc3}, cc4 = {cc4}, pe1 = {pe1}, pe2 = {pe2}, pe3 = {pe3}, 
                      education = {education}, job = {job}, end_time = {datetime.datetime.now()} anmerkungen = {anm} to user {user_id}""")
            return hide_mrkdwn, show_block_part, hide_block_part
        
    def show_text(user_id, wants_choices_db, wants_choices):
        try:
            with db.conn:
                update_state(user_id, wants_choices_db, wants_choices)
        except psycopg2.Error as e:
            print(f"Transaction error occured: {e}, USER: {user_id}, DB_ITEM: {wants_choices_db}, RESPONSE: {wants_choices}")
        if wants_choices != "Nein":
            return show_txtbx
        else:
            return hide_txtbx


    consent_given.select(initial_info, [consent_given, prolific_id], [informed_consent, situation_information, ausgefuellt, consent_given, user_id, condition])
    to_conv.click(ch.start_conv, [user_id, chat_id, turn_id, conv_state, readiness_to_change_start_state], 
                    [chatbot, chat_id, turn_id, user_id, conv_state, situation_information, ausgefuellt_likert]).then(
        ch.greet, [chatbot, chat_id, turn_id], chatbot).then(ch.enable_dropdown, [chatbot, readiness_to_change_start], topic_choice)
    topic_choice.select(ch.set_topic, [topic_choice, chatbot, chat_id, turn_id], [chatbot, topic, turn_id, topic_choice, reason_for_change]).then(
        ch.ask_next, [topic, chatbot, chat_id, turn_id], chatbot)
    upvote_btn.click(ch.disable_buttons,[upvote_btn, turn_id, chat_id], [button_row, explanation, button_text])
    downvote_btn.click(ch.disable_buttons,[downvote_btn, turn_id, chat_id] ,[button_row, explanation, button_text])
    flag_btn.click(ch.disable_buttons,[flag_btn, turn_id, chat_id],[button_row, explanation, button_text])
    reason_for_change.submit(ch.get_initial_text_input, [reason_for_change, chat_id, turn_id, chatbot], [turn_id, chatbot, reason_for_change]).then(
        ch.trigger_likert, reason_for_change, [reason_for_change, likert]).then(
        ch.ask_likert_q, [chatbot,chat_id, turn_id], chatbot)
    likert.release(ch.save_likert, [likert, turn_id, chat_id, chatbot, conv_state], [likert, turn_id, msg, chatbot, conv_state]).then(
        ch.ask_explanation, [likert, chatbot, turn_id, chat_id], chatbot)#.then(start_elicitation, chatbot, [upvote_btn, downvote_btn, flag_btn])
    explanation.submit(ch.add_rating_explanation, [explanation, turn_id, chat_id], [explanation, explanation, msg, msg])
                                               # user_message, history, turn_id, chat_id, previous_turn_type, conv_state, condition, user_id
    msg.submit(ch.disable_text, [msg], [msg]).then(ch.user, [msg, chatbot, turn_id, chat_id, previous_turn_type, conv_state, condition],[msg, msg, chatbot, turn_id, appropriate_action, action_description, previous_turn_type, conv_state], queue=False).then(
        ch.bot, [msg, chatbot, turn_id, chat_id, topic, appropriate_action, action_description, conv_state, condition], chatbot
        ).then(ch.show_buttons, [conv_state, button_text], [button_text, button_row]
               ).then(ch.check_conv_end, [conv_state], [to_post_test])
    
    to_post_test.click(move_to_post_test, [to_post_test], [chatbot, to_post_test, post_test])
    
    education.input(update_state, [user_id, education_state, education], [education_state])
    job.input(update_state, [user_id, job_state, job], [job_state])
    identification.release(update_state, [user_id, identification_state, identification], [identification_state])
    change_pref.release(update_state, [user_id, change_pref_state, change_pref], [change_pref_state])
    readiness_to_change_start.release(update_state, [user_id, readiness_to_change_start_state, readiness_to_change_start], 
                                      [readiness_to_change_start_state])
    readiness_to_change_end.release(update_state, [user_id, readiness_to_change_end_state, readiness_to_change_end], 
                                    [readiness_to_change_end_state])
    #dropdown_suggestions.input(update_state, [user_id, dropdown_suggestions_db, dropdown_suggestions], [])

    ta1.change(update_state, [user_id, ta1_state, ta1], [ta1_state])
    ta2.change(update_state, [user_id, ta2_state, ta2], [ta2_state])
    ta3.change(update_state, [user_id, ta3_state, ta3], [ta3_state])
    ta4.change(update_state, [user_id, ta4_state, ta4], [ta4_state])
    ta5.change(update_state, [user_id, ta5_state, ta5], [ta5_state])
    ta6.change(update_state, [user_id, ta6_state, ta6], [ta6_state])
    ta7.change(update_state, [user_id, ta7_state, ta7], [ta7_state])
    ta8.change(update_state, [user_id, ta8_state, ta8], [ta8_state])
    ta9.change(update_state, [user_id, ta9_state, ta9], [ta9_state])
    ta10.change(update_state, [user_id, ta10_state, ta10], [ta10_state])
    ta11.change(update_state, [user_id, ta11_state, ta11], [ta11_state])
    ta12.change(update_state, [user_id, ta12_state, ta12], [ta12_state])

    FA_S1.change(update_state, [user_id, fa_s1_state, FA_S1], [fa_s1_state])
    FA_S2.change(update_state, [user_id, fa_s2_state, FA_S2], [fa_s2_state])
    FA_S3.change(update_state, [user_id, fa_s3_state, FA_S3], [fa_s3_state])

    PU_S1.change(update_state, [user_id, pu_s1_state, PU_S1], [pu_s1_state])
    PU_S2.change(update_state, [user_id, pu_s2_state, PU_S2], [pu_s2_state])
    PU_S3.change(update_state, [user_id, pu_s3_state, PU_S3], [pu_s3_state])

    attention.change(update_state, [user_id, attention_state, attention], [attention_state])

    RW_S1.change(update_state, [user_id, rw_s1_state, RW_S1], [rw_s1_state])
    RW_S2.change(update_state, [user_id, rw_s2_state, RW_S2], [rw_s2_state])
    RW_S3.change(update_state, [user_id, rw_s3_state, RW_S3], [rw_s3_state])

    pm_1.change(update_state, [user_id, pm_1_state, pm_1], [pm_1_state])
    pm_2.change(update_state, [user_id, pm_2_state, pm_2], [pm_2_state])
    pm_3.change(update_state, [user_id, pm_3_state, pm_3], [pm_3_state])
    pm_4.change(update_state, [user_id, pm_4_state, pm_4], [pm_4_state])
    pm_5.change(update_state, [user_id, pm_5_state, pm_5], [pm_5_state])
    pm_6.change(update_state, [user_id, pm_6_state, pm_6], [pm_6_state])
    pm_7.change(update_state, [user_id, pm_7_state, pm_7], [pm_7_state])
    pm_8.change(update_state, [user_id, pm_8_state, pm_8], [pm_8_state])
    pm_9.change(update_state, [user_id, pm_9_state, pm_9], [pm_9_state])
    pm_10.change(update_state, [user_id, pm_10_state, pm_10], [pm_10_state])
    pm_11.change(update_state, [user_id, pm_11_state, pm_11], [pm_11_state])

    cc1.change(update_state, [user_id, cc1_state, cc1], [cc1_state])
    cc2.change(update_state, [user_id, cc2_state, cc2], [cc2_state])
    cc3.change(update_state, [user_id, cc3_state, cc3], [cc3_state])
    cc4.change(update_state, [user_id, cc4_state, cc4], [cc4_state])

    pe1.change(update_state, [user_id, pe1_state, pe1], [pe1_state])
    pe2.change(update_state, [user_id, pe2_state, pe2], [pe2_state])
    pe3.change(update_state, [user_id, pe3_state, pe3], [pe3_state])

    #anm.input(update_state, [user_id, anm_state, anm], [anm_state])

    ## Form Validation

    to_ta.click(check_post_test, [identification_state, change_pref_state,
                                  readiness_to_change_end_state, user_id], 
                [ausgefuellt_likert, therapeutic_alignment, post_test])

    to_engagement.click(check_ta, [ta1_state, ta2_state, ta3_state, ta4_state,
                                   ta5_state, ta6_state, ta7_state, ta8_state, ta9_state,
                                    ta10_state, ta11_state, ta12_state, user_id],
                                   [ausgefuellt, user_engagement, therapeutic_alignment])
    
    to_perception.click(check_ues, [fa_s1_state, fa_s2_state, fa_s3_state,  
                                    pu_s1_state, pu_s2_state, pu_s3_state,
                                    rw_s1_state, rw_s2_state, rw_s3_state, 
                                    attention_state, user_id],
                                    [ausgefuellt, perception_mi, user_engagement])
    
    to_competence.click(check_mi, [pm_1_state, pm_2_state, pm_3_state, 
                                   pm_4_state, pm_5_state, pm_6_state,  
                                   pm_7_state, pm_8_state, pm_9_state, 
                                   pm_10_state, pm_11_state, user_id], 
                                   [ausgefuellt, comp_emp_pilot, perception_mi])
    
    to_final_page.click(check_comp_emp_pilot, [user_id, cc1_state, cc2_state, cc3_state, cc4_state, 
                                               pe1_state, pe2_state, pe3_state,
                                               education_state, job_state, job, anm], [ausgefuellt, final_page, comp_emp_pilot])
    

demo.queue(concurrency_count=10)
demo.launch(share=True)