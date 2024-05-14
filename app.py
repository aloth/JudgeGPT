import streamlit as st
import uuid
import json
import codecs
import urllib.request
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from streamlit_javascript import st_javascript

def save_participant(language, age, gender, political_view, is_native_speaker, education_level, newspaper_subscription, fnews_experience, screen_resolution, ip_location, user_agent, query_params):
    """
    Saves participant details to session state and MongoDB for persistence.
    """
    participant = {
        "ParticipantID": st.session_state.user_id,
        "ISOLanguage": language,
        "Age": age,
        "Gender": gender,
        "PoliticalView": political_view,
        "IsNativeSpeaker": is_native_speaker,
        "EducationLevel": education_level,
        "NewspaperSubscription": newspaper_subscription,
        "FNewsExperience": fnews_experience,
        "ScreenResolution": screen_resolution,
        "IpLocation": ip_location,
        "UserAgent": user_agent,
        "QueryParams": query_params
    }

    # Connecting to MongoDB to save participant data.
    with MongoClient(st.secrets["mongo"].connection,server_api=ServerApi('1')) as client:
        db = client.realorfake
        collection = db.participants
        collection.insert_one(participant)
    
    # Updating session state with participant data.
    st.session_state.participant = participant

def save_response(fragment_id, human_machine_score, legit_fake_score, topic_knowledge_score, time_to_answer):
    """
    Saves survey response to session state and MongoDB.
    """
    response = {
        "ResultID": uuid.uuid4().hex,
        "ParticipantID": st.session_state.user_id,
        "FragmentID": fragment_id,
        "HumanMachineScore": human_machine_score,
        "LegitFakeScore": legit_fake_score,
        "TopicKnowledgeScore": topic_knowledge_score,
        "Timestamp": datetime.now().isoformat(),
        "TimeToAnswer": time_to_answer,
        "SessionCount": st.session_state.count
    }
    
    # Connecting to MongoDB to save response data.
    with MongoClient(st.secrets["mongo"].connection,server_api=ServerApi('1')) as client:
        db = client.realorfake
        collection = db.results
        collection.insert_one(response)
    
    # Updating session state with the new response.
    st.session_state.responses.append(response)


def retrieve_fragments(ISOLanguage):
    """
    Retrieves a set of news fragments from MongoDB based on the participant's language preference.
    """
    with st.spinner('Retrieving from database...'):
        with MongoClient(st.secrets["mongo"].connection, server_api=ServerApi('1')) as client:
            db = client.realorfake
            collection = db.fragments

            # Aggregation pipeline to filter, project, and randomly sample news fragments.
            pipeline = [
                {"$match": {"ISOLanguage": ISOLanguage}},
                {"$project": {"FragmentID": 1, "Content": 1, "_id": 0}},  # Project only FragmentID and Content
                {"$sample": {"size": 50}}
            ]
            fragments = collection.aggregate(pipeline)
            st.success("Data retrieved.")
            return list(fragments)

def get_user_agent():
    """
    Retrieves the browser's user agent string using JavaScript.
    """
    try:
        user_agent = st_javascript('navigator.userAgent')
        if user_agent: return user_agent
        else: return None
    except: return None

def get_screen_resolution():
    """
    Retrieves the device's screen resolution using JavaScript.
    """
    script = '({width: window.screen.width, height: window.screen.height})'
    try:
        screen_resolution = st_javascript(script)
        if screen_resolution: return screen_resolution
        else: return None
    except: return None

def get_ip_location():
    """
    Retrieves the participant's IP location using an external API and JavaScript fetch.
    """
    url = 'https://freeipapi.com/api/json'
    script = (f'await fetch("{url}").then('
                'function(response) {'
                    'return response.json();'
                '})')
    try:
        ip_location = st_javascript(script)
        if ip_location: return ip_location
        else: return None
    except: return None

def display_intro():
    """
    Displays main title and intro.
    """
    st.subheader("🔍 Real or Fake: Can You Spot Misinformation?")
    st.markdown("""
    **Challenge your ability to distinguish between authentic news and AI-generated fake news in our interactive quiz.**
    Dive into the complex world where generative AI blurs the lines between reality and fiction. Learn more about the impact of Generative AI on fake news through our [open access paper](https://arxiv.org/abs/2404.03021) and explore our research at [Cyber CNI](https://cybercni.fr/research/lutte-informatique-dinfluence-l2i-fake-news-detection-generation-prevention/).
    """)

    with st.expander("FAQs & Useful Info", expanded=False):
        st.markdown("""
            - **Privacy Concerns?** Email us at alexander.loth@stud.fra-uas.de with your participant ID to request data deletion within one year of submission. Use 'Delete Request' as your subject line.
            - **No Downloads Needed:** Access the quiz directly from your browser.
            - **Experiencing Delays?** High traffic might slow down the website. Try revisiting later.
            - **AI-Generated Content:** Some headlines are crafted by AI, potentially carrying biases based on the data they were trained on.
            """)

def display_participant_id():
    """
    Displays participant ID.
    """
    st.markdown(f'<p style="font-size: 12px;">Your participant ID: {st.session_state.user_id}</p>', unsafe_allow_html=True)

def print_consent_info():
    """
    Display consent information.
    """
    consent_request = st.empty()
    with consent_request.container():
        with st.expander("Consent / GDPR / Imprint", expanded=False):
            tab1, tab2, tab3, tab4 = st.tabs(["Consent", "GDPR", "Imprint", "License"])

            with tab1:
                st.markdown("#### Join Our Study on Generative AI and Fake News")
                st.markdown("""
                    By participating in our survey, you'll evaluate various statements, discerning between what's real or fake, and whether they're crafted by humans or machines.
                    
                    **Eligibility and Voluntary Participation:** Anyone is welcome to partake in this significant exploration. Your involvement is completely voluntary and immensely valued.

                    This initiative is spearheaded by Alexander Loth, Prof. Martin Kappes, and Prof. Marc-Oliver Pahl. For inquiries or additional details, please don't hesitate to get in touch.
                    """)

                st.markdown("##### Your Privacy")
                st.markdown("""
                    Your privacy is important. By participating, you are providing anonymous responses and demographic information. In addition, you agree that your location will be determined by your IP address and that your browser information will be collected. This information is critical to understanding how people interact with misinformation. We guarantee the confidentiality of your data, which will be aggregated for research purposes. 
                    
                    **Should you wish to retract your data post-participation, you'll be equipped with an anonymous participant ID for this process.**
                """)

                st.markdown("##### Ready to Make a Difference?")
                st.markdown("**By consenting to participate, you're agreeing to contribute anonymized data to our study. Are you ready to join us in this critical research effort?**")

            with tab2:
                st.header("GDPR")
                print_file_content("https://raw.githubusercontent.com/aloth/JudgeGPT/main/README.md")

            with tab3:
                st.header("Imprint")
                print_file_content("https://raw.githubusercontent.com/aloth/JudgeGPT/main/README.md")

            with tab4:
                st.header("License")
                print_file_content("https://raw.githubusercontent.com/aloth/JudgeGPT/main/LICENSE")

def print_file_content(url):
    """
    Prints content of a file.
    """
    for line in urllib.request.urlopen(url):
        st.markdown(line.decode('utf-8'))

# Configure the Streamlit page with a title and icon.
st.set_page_config(
    page_title="Real or Fake?",
    page_icon="🙈"
)

# Main title displayed at the top of the survey page.
display_intro()

# Retrieve essential data using JavaScript integrations.
screen_resolution=get_screen_resolution()
ip_location=get_ip_location()
user_agent=get_user_agent()

# Get query parameters
query_params = st.query_params

# Initialize session state variables if they're not already set.
if 'user_id' not in st.session_state:
    st.session_state.user_id = uuid.uuid4().hex
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'participant' not in st.session_state:
    st.session_state.participant = []

# Collecting participant information through a form.
if not st.session_state.form_submitted:
    #consent = ask_for_consent()

    #if consent:
    with st.form("participant_info", clear_on_submit=True):

        # Define allowed languages
        allowed_languages = ["en", "fr", "de", "es"]

        # Initialize default language
        default_language = "en"

        try:
            # Extract the language query parameter, ensuring it's a list and not empty
            language_param = query_params.get("language", [])

            # Check if the extracted language parameter is non-empty and if it is in allowed languages
            if language_param and language_param.lower() in allowed_languages:
                # Set the default language, converted to lower case for matching
                default_language = language_param.lower()
            else:
                # Check if 'countryCode' is in ip_location and if it is in the allowed languages          
                if 'countryCode' in ip_location and ip_location['countryCode'].lower() in allowed_languages:
                    # Set the default language, converted to lower case for matching
                    default_language = ip_location['countryCode'].lower()
        except:
            st.status("Trying to determine user language...")

        # Display the selectbox with the determined default language
        language = st.selectbox("Language", allowed_languages, index=allowed_languages.index(default_language))

        # Age selection
        age_default = 1.11
        age = st.slider(
            label = "Age",
            min_value = 1.0,
            max_value = 133.0,
            value = age_default,
            step = 1.0,
            format = "%d years"
        )
        
        # Gender selection
        gender = st.selectbox(
            label = "Gender",
            options = ["Male", "Female", "Other", "Prefer not to say"],
            index = None,
            placeholder="Choose an option"
        )

        # Political view selection
        political_view_default = 0.5
        political_view_options = {
            0.0: "Far Left",
            0.2: "Left",
            0.4: "Center-Left",
            0.5: "Choose an option",  # Placeholder option
            0.6: "Center-Right",
            0.8: "Right",
            1.0: "Far Right"
        }
        political_view = st.select_slider(
            label = "How do you assess your political view?",
            options = list(political_view_options.keys()),
            format_func = lambda x: political_view_options[x],
            value = political_view_default
        )

        # Native speaker selection
        is_native_speaker = st.selectbox(
            label = "Are you a native speaker?",
            options = ["Yes", "No"],
            index = None,
            placeholder="Choose an option"
        )

        # Education level selection
        education_level = st.selectbox(
            label = "Highest level of education attained",
            options = ["None", "High School", "Apprenticeship", "Bachelor's Degree", "Master's Degree", "Doctoral Degree"],
            index = None,
            placeholder="Choose an option"
        )

        # Newspaper subscription selection
        newspaper_subscription_default = 1.5
        newspaper_subscription_options = {
            0.0: "None",
            1.0: "One",
            1.5: "Choose an option",  # Placeholder option
            2.0: "Two",
            3.0: "Three or more"
        }
        newspaper_subscription = st.select_slider(
            label = "Number of newspaper subscriptions",
            options = list(newspaper_subscription_options.keys()),
            format_func = lambda x: newspaper_subscription_options[x],
            value = newspaper_subscription_default
        )

        # Newspaper subscription selection
        fnews_experience_default = 0.5
        fnews_experience_options = {
            0.0: "Completely unfamiliar",
            0.2: "Mostly unfamiliar",
            0.4: "Somewhat unfamiliar",
            0.5: "Choose an option",  # Placeholder option
            0.6: "Somewhat familiar",
            0.8: "Mostly familiar",
            1.0: "Completely familiar"
        }
        fnews_experience = st.select_slider(
            label = "Your experience with fake news",
            options = list(fnews_experience_options.keys()),
            format_func = lambda x: fnews_experience_options[x],
            value = fnews_experience_default
        )

        # Asking for consent
        print_consent_info()
        consent_option = st.toggle(
                label = "Yes, I'm in! I consent to participate.",
                value = False,
                key = "consent",
                label_visibility = "visible"
            )
        
        # Display participant ID
        display_participant_id()

        # Submit button for the form.
        submitted = st.form_submit_button("Start Survey", disabled=consent_option)
        
        if submitted:
            validity = True
            # Validity checks
            if age == age_default:
                st.error("Please confirm your age.")
                validity = False
            if not gender:
                st.error("Please confirm your gender.")
                validity = False  
            if political_view == political_view_default:
                st.error("Please confirm how you assess your political view.")
                validity = False
            if not is_native_speaker:
                st.error("Please confirm if you are a native speaker.")
                validity = False
            if not education_level:
                st.error("Please confirm your education level.")
                validity = False
            if newspaper_subscription == newspaper_subscription_default:
                st.error("Please confirm how many newspapers you have subscribed.")
                validity = False
            if fnews_experience == fnews_experience_default:
                st.error("Please confirm how you assess your experience with fake news.")
                validity = False
            if not consent_option:
                st.error("Please give your consent.")
                validity = False  
            if validity:
                # Save participant data and mark the survey as started.
                with st.spinner('Wait for it...'):
                    save_participant(language, age, gender, political_view, is_native_speaker, education_level, newspaper_subscription, fnews_experience, screen_resolution, ip_location, user_agent, query_params)
                    st.session_state.form_submitted = True
                    st.session_state.start_time = datetime.now()
                st.success('Done!')
                st.rerun()

# Main survey logic to display once the participant information form is submitted.
if st.session_state.form_submitted:
    # Initialize additional session state variables for survey progression.
    if 'current_fragment_index' not in st.session_state:
        st.session_state.current_fragment_index = 0
    if 'count' not in st.session_state:
        st.session_state.count = 1
    if 'responses' not in st.session_state:
        st.session_state.responses = []
    if 'fragments' not in st.session_state:
        # Retrieve news fragments based on participant's language preference.
        st.session_state.fragments = retrieve_fragments(st.session_state.participant["ISOLanguage"])

    # Check if it's necessary to fetch more fragments and reset index if so.
    if st.session_state.current_fragment_index >= len(st.session_state.fragments):
        st.session_state.fragments = retrieve_fragments(st.session_state.participant["ISOLanguage"])  # Reload or fetch new data
        st.session_state.current_fragment_index = 0  # Reset index to start from the first fragment of the new set

    # Display the current news fragment and collect responses.
    if st.session_state.form_submitted:
        current_fragment = st.session_state.fragments[st.session_state.current_fragment_index]
        with st.form(key=f"news_fragment_{current_fragment['FragmentID']}"):
            st.write(current_fragment['Content'].encode('utf-16', 'surrogatepass').decode('utf-16'))
            st.divider()

            # Define the options for the Human vs. Machine Generated Score
            human_machine_score_default = 0.5
            human_machine_score_options = {
                0.0: "Definetly Human Generated",
                0.2: "Probalby Human Generated",
                0.4: "Likey Human Generated",
                0.5: "Choose an option",  # Placeholder option
                0.6: "Likey Machine Generated",
                0.8: "Probalby Machine Generated",
                1.0: "Definetly Machine Generated"
            }

            # Create the slider for the participant to rate whether they believe the news was generated by a human or machine
            human_machine_score = st.select_slider(
                label = "Human or Machine Generated?",
                options = list(human_machine_score_options.keys()),
                format_func = lambda x: human_machine_score_options[x],
                key = f"hm_score_{current_fragment['FragmentID']}",
                value = human_machine_score_default
            )

            # Define the options for the Legitimacy Score
            legit_fake_score_default = 0.5
            legit_fake_score_options = {
                0.0: "Definetly Legit News",
                0.2: "Probalby Legit News",
                0.4: "Likey Legit News",
                0.5: "Choose an option",  # Placeholder option
                0.6: "Likey Fake News",
                0.8: "Probalby Fake News",
                1.0: "Definetly Fake News"
            }

            # Create the slider for the participant to rate the perceived legitimacy of the news
            legit_fake_score = st.select_slider(
                label = "Legit or Fake News?",
                options = list(legit_fake_score_options.keys()),
                format_func = lambda x: legit_fake_score_options[x],
                key = f"lf_score_{current_fragment['FragmentID']}",
                value = legit_fake_score_default
            )

            # Define the options for the knowledge about the topic
            topic_knowledge_score_default = 0.5
            topic_knowledge_score_options = {
                0.0: "Not at all",
                0.2: "Slightly",
                0.4: "Somewhat",
                0.5: "Choose an option",  # Placeholder option
                0.6: "Fairly well",
                0.8: "Very well",
                1.0: "Extremely well"
            }

            # Create the slider for participants to rate their knowledge on the topic
            topic_knowledge_score = st.select_slider(
                label = "How familiar are you with the topic covered in this news?",
                options = list(topic_knowledge_score_options.keys()),
                format_func = lambda x: topic_knowledge_score_options[x],
                key = f"topic_knowledge_{current_fragment['FragmentID']}",
                value = topic_knowledge_score_default
            )

            st.divider()
            st.write("This is your respone no.", st.session_state.count)

            # Display participant ID
            display_participant_id()

            # Submit button for each news fragment response.
            submitted = st.form_submit_button("Submit Response")
            if submitted:
                validity = True
                # Validity checks
                if human_machine_score == human_machine_score_default:
                    st.error("Please confirm how you assess if this news is human or machine generated.")
                    validity = False
                if legit_fake_score == legit_fake_score_default:
                    st.error("Please confirm how you assess if this news is legit or fake.")
                    validity = False
                if topic_knowledge_score == topic_knowledge_score_default:
                    st.error("Please confirm how you assess your topic knowledge.")
                    validity = False
                if validity:
                    with st.spinner('Wait for it...'):
                        # Calculate the time taken to answer this fragment.
                        end_time = datetime.now()
                        time_to_answer = (end_time - st.session_state.start_time).total_seconds()

                        # Save the response to the database and session state.
                        save_response(current_fragment['FragmentID'], human_machine_score, legit_fake_score, topic_knowledge_score, time_to_answer)
                        
                        # Increment the fragment index and response count for the session.
                        st.session_state.current_fragment_index = (st.session_state.current_fragment_index + 1) % len(st.session_state.fragments)
                        st.session_state.count = st.session_state.count + 1

                        # Reset the start time for the next fragment's response timing.
                        st.session_state.start_time = datetime.now()
                    
                    st.success('Done!')
                    st.rerun()
