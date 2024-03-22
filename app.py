import streamlit as st
import uuid
import json
import codecs
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

# Configure the Streamlit page with a title and icon.
st.set_page_config(
    page_title="Real or Fake?",
    page_icon="🙈"
)

# Main title displayed at the top of the survey page.
st.title("Participant Survey for Fake News Research")

st.write()

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

        #language = st.selectbox("Language", ["en", "fr", "de", "es"])
        age = st.slider("Age", 1, 133, 33)
        gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])

        political_view_options = {
            0.0: "Far Left",
            0.25: "Left",
            0.4: "Center-Left",
            0.5: "Center",
            0.6: "Center-Right",
            0.75: "Right",
            1.0: "Far Right"
        }
        political_view = st.select_slider("Political view", options=list(political_view_options.keys()), format_func=lambda x: political_view_options[x], value=0.5)
        is_native_speaker = st.radio("Are you a native speaker?", ("Yes", "No"))
        education_level = st.selectbox("Highest level of education attained", ["None", "High School", "Apprenticeship", "Bachelor's Degree", "Master's Degree", "Doctoral Degree"])
        newspaper_subscription = st.select_slider("Number of newspaper subscriptions", options=["None", "One", "Two", "Three or more"])

        fnews_experience_options = {
            0.0: "None",
            0.25: "Low",
            0.5: "Moderate",
            0.75: "High",
            1.0: "Plenty"
        }
        fnews_experience = st.select_slider("Your experience with fake news", options=list(fnews_experience_options.keys()), format_func=lambda x: fnews_experience_options[x], value=0.0)

        # Submit button for the form.
        submitted = st.form_submit_button("Start Survey")
        if submitted:
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
            human_machine_score_options = {
                0.0: "Definetly Human Generated",
                0.2: "Probalby Human Generated",
                0.4: "Likey Human Generated",
                0.6: "Likey Machine Generated",
                0.8: "Probalby Machine Generated",
                1.0: "Definetly Machine Generated"
            }

            # Create the slider for the participant to rate whether they believe the news was generated by a human or machine
            human_machine_score = st.select_slider(
                "Human or Machine Generated?",
                options=list(human_machine_score_options.keys()),
                format_func=lambda x: human_machine_score_options[x],
                key=f"hm_score_{current_fragment['FragmentID']}"
            )

            # Define the options for the Legitimacy Score
            legit_fake_score_options = {
                0.0: "Definetly Legit News",
                0.2: "Probalby Legit News",
                0.4: "Likey Legit News",
                0.6: "Likey Fake News",
                0.8: "Probalby Fake News",
                1.0: "Definetly Fake News"
            }

            # Create the slider for the participant to rate the perceived legitimacy of the news
            legit_fake_score = st.select_slider(
                "Legit or Fake News?",
                options=list(legit_fake_score_options.keys()),
                format_func=lambda x: legit_fake_score_options[x],
                key=f"lf_score_{current_fragment['FragmentID']}"
            )

            # Define the options for the knowledge about the topic
            topic_knowledge_options = {
                0.0: "Not at all",
                0.2: "Slightly",
                0.4: "Somewhat",
                0.6: "Fairly well",
                0.8: "Very well",
                1.0: "Extremely well"
            }

            # Create the slider for participants to rate their knowledge on the topic
            topic_knowledge_score = st.select_slider(
                "How familiar are you with the topic covered in this news?",
                options=list(topic_knowledge_options.keys()),
                format_func=lambda x: topic_knowledge_options[x],
                key=f"topic_knowledge_{current_fragment['FragmentID']}"
            )

            st.divider()
            st.write("This is your respone no.", st.session_state.count)

            # Submit button for each news fragment response.
            submitted = st.form_submit_button("Submit Response")
            if submitted:
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
