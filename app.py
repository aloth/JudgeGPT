import streamlit as st
import pandas as pd
import uuid
import json
import codecs
import urllib.request
import gettext
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from streamlit_javascript import st_javascript

__name__ = "JudgeGPT"
__version__ = "0.9"
__author__ = "Alexander Loth"
__email__ = "alexander.loth@stud.fra-uas.de"
__report_a_bug__ = "https://github.com/aloth/JudgeGPT/issues"

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

def save_response(fragment_id, human_machine_score, legit_fake_score, topic_knowledge_score, time_to_answer, origin, is_fake):
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
        "SessionCount": st.session_state.count,
        "Origin": origin,
        "IsFake": is_fake
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
    with st.spinner(_("Retrieving from database...")):
        with MongoClient(st.secrets["mongo"].connection, server_api=ServerApi('1')) as client:
            db = client.realorfake
            collection = db.fragments

            # Aggregation pipeline to filter, project, and randomly sample news fragments.
            pipeline = [
                {"$match": {"ISOLanguage": ISOLanguage}},
                {"$project": {
                    "FragmentID": 1,
                    "Content": 1,
                    "Origin": 1,
                    "IsFake": 1,
                    "_id": 0
                    }},  # Project only required attributes
                {"$sample": {"size": 50}}
            ]
            fragments = collection.aggregate(pipeline)
            st.toast(_("Data retrieved."))
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
    st.subheader("🔍 " + _("Real or Fake: Can You Spot Misinformation?"))
    st.markdown(_("**Challenge your ability to distinguish between authentic news and AI-generated fake news in our interactive quiz.**"))
    st.markdown(_("Dive into the complex world where generative AI blurs the lines between reality and fiction. Learn more about the impact of Generative AI on fake news through our [open access paper](https://arxiv.org/abs/2404.03021) and explore our research at [Cyber CNI](https://cybercni.fr/research/lutte-informatique-dinfluence-l2i-fake-news-detection-generation-prevention/)."))

    with st.expander(_("FAQs & Useful Info"), expanded=False):
        st.markdown(_("- **Privacy Concerns?** Email us at alexander.loth@stud.fra-uas.de with your participant ID to request data deletion within one year of submission. Use 'Delete Request' as your subject line."))
        st.markdown(_("- **No Downloads Needed:** Access the quiz directly from your browser."))
        st.markdown(_("- **Experiencing Delays?** High traffic might slow down the website. Try revisiting later."))
        st.markdown(_("- **AI-Generated Content:** Some headlines are crafted by AI, potentially carrying biases based on the data they were trained on."))

def display_participant_id():
    """
    Displays participant ID.
    """
    st.markdown(
        '<p style="font-size: 12px;">' + _("Your participant ID:") + " " + st.session_state.user_id + '</p>',
        unsafe_allow_html=True
    )

def display_consent_box():
    """
    Display consent information.
    """
    consent_request = st.empty()
    with consent_request.container():
        with st.expander(_("Consent / About / Privacy Policy / Imprint / License"), expanded=False):
            consent_tab, about_tab, privacy_policy_tab, imprint_tab, license_tab = st.tabs([
                _("Consent"),
                _("About"),
                _("Privacy Policy"),
                _("Imprint"),
                _("License")
            ])

            with consent_tab:
                print_md_files("docs/consent.md", "consent.md")

            with about_tab:
                print_md_files("README.md", "README.md")

            with privacy_policy_tab:
                print_md_files("docs/privacypolicy.md", "privacypolicy.md")

            with imprint_tab:
                print_md_files("docs/imprint.md", "imprint.md")

            with license_tab:
                print_md_files("LICENSE")

def load_file(url):
    """
    Fetch and decode the content from the URL.
    """
    content = ""

    try:
        for line in urllib.request.urlopen(url):
            content += line.decode('utf-8')
    except:
        content = None

    return content

def print_md_files(file_en, file_int = None):
    """
    Print content files.
    """
    base_url = "https://raw.githubusercontent.com/aloth/JudgeGPT/main/"

    if file_int:
        content = {}

        # Load the content for each language
        for lang in allowed_languages:
            if lang == "en":
                url = f"{base_url}{file_en}"
            else:
                url = f"{base_url}docs/{lang}/{file_int}"
            
            # Initialize an empty string for the content
            content[lang] = load_file(url)
            if not content[lang]:
                content[lang] = content["en"]

        st.markdown(content[st.session_state.language])
    else:
        url = f"{base_url}{file_en}"
        content = load_file(url)

        st.markdown(content)

def aggregate_results():
    """
    Aggregates results from session state.
    """
    if not st.session_state.responses:
        return "No responses found."

    # Convert the responses to a DataFrame for easy manipulation
    df = pd.DataFrame(st.session_state.responses)

    # Calculate averages
    avg_hm_score = df['HumanMachineScore'].mean()
    avg_lf_score = df['LegitFakeScore'].mean()
    avg_topic_knowledge = df['TopicKnowledgeScore'].mean()

    # Calculate accuracy
    df['HM_Accuracy'] = df.apply(lambda row: 1 if (row['HumanMachineScore'] >= 0.5 and row['Origin'] == "Machine") or 
                                          (row['HumanMachineScore'] < 0.5 and row['Origin'] == "Human") else 0, axis=1)
    df['LF_Accuracy'] = df.apply(lambda row: 1 if (row['LegitFakeScore'] >= 0.5 and row['IsFake']) or 
                                          (row['LegitFakeScore'] < 0.5 and not row['IsFake']) else 0, axis=1)
    hm_accuracy = df['HM_Accuracy'].mean()
    lf_accuracy = df['LF_Accuracy'].mean()

    # Prepare the results summary
    summary = {
        "Total Responses": len(df),
        "Average Human/Machine Score": avg_hm_score,
        "Average Legitimacy Score": avg_lf_score,
        "Average Topic Knowledge": avg_topic_knowledge,
        "Human/Machine Accuracy": hm_accuracy,
        "Legitimacy Accuracy": lf_accuracy
    }

    return summary

def display_aggregate_results():
    """
    Displays results from session state.
    """
    completed_response_count = st.session_state.count - 1
    if completed_response_count % 5 == 0 and completed_response_count != 0:
        results = aggregate_results()
        st.balloons()
        st.write("🎉 " + _("Congratulations! You've completed {completed_responses} responses. Here are your results so far:").format(completed_responses=results['Total Responses']))
        # st.write(f"Average Human/Machine Score: {results['Average Human/Machine Score']:.2f}")
        # st.write(f"Average Legitimacy Score: {results['Average Legitimacy Score']:.2f}")
        # st.write(f"Average Topic Knowledge: {results['Average Topic Knowledge']:.2f}")
        st.write("🤖 " + _("Human/Machine Accuracy:") + f" {results['Human/Machine Accuracy'] * 100:.2f}%")
        st.write("🤔 " + _("Legitimacy Accuracy:") + f" {results['Legitimacy Accuracy'] * 100:.2f}%")

        badge1, badge2 = st.columns(2)
        with badge1:
            # Display badge for high Human/Machine Accuracy
            if results['Human/Machine Accuracy'] >= 0.7:
                st.image("images/judgegpt_badge.jpg")
                st.write("🎖️ " + _("You've earned the JudgeGPT badge for achieving high accuracy in identifying Human/Machine generated content!") + " 🎉")
        
        with badge2:
            # Display badge for high Legitimacy Accuracy
            if results['Legitimacy Accuracy'] >= 0.7:
                st.image("images/judgegpt_badge.jpg")
                st.write("🎖️ " + _("You've earned the JudgeGPT badge for achieving high accuracy in identifying Legit/Fake news!") + " 🎉")

    else:
        remaining_responses = 5 - (completed_response_count % 5)
        if remaining_responses == 1:
            message = _("Only {remaining_responses} more response to see your results! Keep going!")
        else:
            message = _("Only {remaining_responses} more responses to see your results! Keep going!")
        st.write("👍 " + message.format(remaining_responses=remaining_responses) + " 🚀")

def get_translator(lang: str = "en"):
    """
    Initializes of the translator with English as fallback.
    """
    if lang == "en":
        # For English, return the identity function (no translation needed)
        return lambda x: x
    else:
        try:
            # Load the translation files
            trans = gettext.translation("base", localedir = "locales", languages = [lang])
            trans.install()  # Install the translation in the global namespace
            return trans.gettext  # Return the gettext method from the translation object
        except FileNotFoundError:
            print("DEBUG: Translation file not found. Please check the path and language settings.")
            return lambda x: x  # Return a dummy translator function

def get_language_from_url(query_params, allowed_languages):
    """
    Checks if a available language is set in the URL query. 
    """
    try:
        language_param = query_params.get("language", [])

        # Check if the extracted language parameter is non-empty and if it is in allowed languages
        if language_param and language_param.lower() in allowed_languages:
            # Set the default language, converted to lower case for matching
            url_language = language_param.lower()
        return url_language
    except:
        return None
    
def display_feedback_button():
    # CSS for the feedback button
    feedback_button_css = """
    <style>
        @media screen and (min-width: 768px) {
            .feedback-button {
                position: fixed;
                right: 10px;
                top: 50%;
                transform: translateY(-50%) rotate(-90deg);
                background-color: #ff5733;
                color: white;
                padding: 10px 20px;
                border-radius: 50px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
                transition: background-color 0.3s, transform 0.3s;
            }
            .feedback-button:hover {
                background-color: #e74c3c;
                transform: translateY(-50%) rotate(-90deg) translateY(-2px);
            }
        }
    </style>
    """
    
    # HTML for the feedback button
    feedback_button_html = """
    <a href="https://docs.google.com/forms/d/e/1FAIpQLSfgO-1Tkq5_f5Poz7dpr1DSXp1bua72aXmhc5KxjFNETNL43g/viewform?usp=sf_link" target="_blank" class="feedback-button">FEEDBACK</a>
    """
    
    # Combine CSS and HTML and render using Streamlit
    st.markdown(feedback_button_css + feedback_button_html, unsafe_allow_html=True)

# Initialize session state variables if they're not already set.
if 'user_id' not in st.session_state:
    st.session_state.user_id = uuid.uuid4().hex
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'participant' not in st.session_state:
    st.session_state.participant = []
if 'language' not in st.session_state:
    st.session_state.language = "en"

# Get query parameters
query_params = st.query_params

# Define allowed languages
allowed_languages = ["en", "fr", "de", "es"]

# Get language from URL auery
url_language = get_language_from_url(query_params, allowed_languages)

# If "language" is set in URL query, use apply it
if url_language:
    st.session_state.language = url_language

# Initialize UI language
ui_language = st.session_state.language

# Initialize the translator
_ = get_translator(st.session_state.language)

# Configure the Streamlit page with a title and icon.
st.set_page_config(
    page_title = _("Real or Fake?"),
    page_icon = "🙈",
        menu_items = {
        'Get Help': f"mailto:{__email__}",
        'Report a bug': __report_a_bug__,
        'About': f"""
            ### {__name__} {__version__}
            #### Author: {__author__}
        """
    }
)

# Debugging output
# st.write(f"Locales directory: {os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locales')}")

# Retrieve essential data using JavaScript integrations.
screen_resolution = get_screen_resolution()
ip_location = get_ip_location()
user_agent = get_user_agent()

# Collecting participant information through a form.
if not st.session_state.form_submitted:
    with st.form("participant_info", clear_on_submit = False):
        # Initialize default language
        default_language = "en"

        # Check if the URL language parameter is set
        if url_language:
            # Set the default language, converted to lower case for matching
            default_language = url_language
        else:
            try:
                # Check if 'countryCode' is in ip_location and if it is in the allowed languages          
                if 'countryCode' in ip_location and ip_location['countryCode'].lower() in allowed_languages:
                    # Set the default language, converted to lower case for matching
                    default_language = ip_location['countryCode'].lower()
                    st.session_state.language = default_language
                    _ = get_translator(default_language)
            except:
                st.status(_("Trying to determine user language..."))

        # Main title displayed at the top of the survey page.
        display_intro()

        # Display the feedback button
        display_feedback_button()

        # Display the selectbox with the determined default language
        languages_options = {
            "en": "English",
            "fr": "French",
            "de": "German",
            "es": "Spanish"
        }
        language = st.selectbox(
            label = _("Language"),
            options = list(languages_options.keys()),
            format_func = lambda x: languages_options[x],
            index = allowed_languages.index(default_language),
            placeholder = _("Choose an option")
        )

        # Age selection
        age_default = 33.33
        age = st.slider(
            label = _("Age"),
            min_value = 16.0,
            max_value = 133.0,
            value = age_default,
            step = 1.0,
            format = _("%d years")
        )
        
        # Gender selection
        gender_options = {
            "Male": _("Male"),
            "Female": _("Female"),
            "Other": _("Other"),
            "Prefer not to say": _("Prefer not to say")
        }
        gender = st.selectbox(
            label = _("Gender"),
            options = list(gender_options.keys()),
            format_func = lambda x: gender_options[x],
            index = None,
            placeholder = _("Choose an option")
        )

        # Political view selection
        political_view_default = 0.5
        political_view_options = {
            0.0: _("Far Left"),
            0.2: _("Left"),
            0.4: _("Center-Left"),
            0.5: _("Choose an option"),  # Placeholder option
            0.6: _("Center-Right"),
            0.8: _("Right"),
            1.0: _("Far Right")
        }
        political_view = st.select_slider(
            label = _("How do you assess your political view?"),
            options = list(political_view_options.keys()),
            format_func = lambda x: political_view_options[x],
            value = political_view_default
        )

        # Native speaker selection
        is_native_speaker_options = {
            "Yes": _("Yes"),
            "No": _("No")
        }
        is_native_speaker = st.selectbox(
            label = _("Are you a native speaker?"),
            options = list(is_native_speaker_options.keys()),
            format_func = lambda x: is_native_speaker_options[x],
            index = None,
            placeholder = _("Choose an option")
        )

        # Education level selection
        education_level_options = {
            "None": _("None"),
            "High School": _("High School"),
            "Apprenticeship": _("Apprenticeship"),
            "Bachelor's Degree": _("Bachelor's Degree"),
            "Master's Degree": _("Master's Degree"),
            "Doctoral Degree": _("Doctoral Degree")
        }
        education_level = st.selectbox(
            label = _("Highest level of education attained"),
            options = list(education_level_options.keys()),
            format_func = lambda x: education_level_options[x],
            index = None,
            placeholder = _("Choose an option")
        )

        # Newspaper subscription selection
        newspaper_subscription_default = 1.5
        newspaper_subscription_options = {
            0.0: _("None"),
            1.0: _("One"),
            1.5: _("Choose an option"),  # Placeholder option
            2.0: _("Two"),
            3.0: _("Three or more")
        }
        newspaper_subscription = st.select_slider(
            label = _("Number of newspaper subscriptions"),
            options = list(newspaper_subscription_options.keys()),
            format_func = lambda x: newspaper_subscription_options[x],
            value = newspaper_subscription_default
        )

        # Newspaper subscription selection
        fnews_experience_default = 0.5
        fnews_experience_options = {
            0.0: _("Completely unfamiliar"),
            0.2: _("Mostly unfamiliar"),
            0.4: _("Somewhat unfamiliar"),
            0.5: _("Choose an option"),  # Placeholder option
            0.6: _("Somewhat familiar"),
            0.8: _("Mostly familiar"),
            1.0: _("Completely familiar")
        }
        fnews_experience = st.select_slider(
            label = _("Your experience with fake news"),
            options = list(fnews_experience_options.keys()),
            format_func = lambda x: fnews_experience_options[x],
            value = fnews_experience_default
        )

        # Asking for consent
        with st.spinner(_("Getting ready...")):
            display_consent_box()
            consent_option = st.toggle(
                    label = _("Yes, I'm in! I consent to participate."),
                    value = False,
                    key = "consent",
                    label_visibility = "visible"
                )
        
        # Display participant ID
        display_participant_id()

        # Submit button for the form.
        submitted = st.form_submit_button(_("Start Survey"))
        
        if submitted:
            validity = True
            # Validity checks
            if age == age_default:
                st.error(_("Please confirm your age."))
                validity = False
            if not gender:
                st.error(_("Please confirm your gender."))
                validity = False  
            if political_view == political_view_default:
                st.error(_("Please confirm how you assess your political view."))
                validity = False
            if not is_native_speaker:
                st.error(_("Please confirm if you are a native speaker."))
                validity = False
            if not education_level:
                st.error(_("Please confirm your education level."))
                validity = False
            if newspaper_subscription == newspaper_subscription_default:
                st.error(_("Please confirm how many newspapers you have subscribed."))
                validity = False
            if fnews_experience == fnews_experience_default:
                st.error(_("Please confirm how you assess your experience with fake news."))
                validity = False
            if not consent_option:
                st.error(_("Please give your consent."))
                validity = False  
            if validity:
                # Save participant data and mark the survey as started.
                with st.spinner(_("Wait for it...")):
                    save_participant(language, age, gender, political_view, is_native_speaker, education_level, newspaper_subscription, fnews_experience, screen_resolution, ip_location, user_agent, query_params)
                    st.session_state.form_submitted = True
                    st.session_state.start_time = datetime.now()
                st.success(_("Done!"))
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
        with st.form(key=f"news_fragment_{current_fragment['FragmentID']}", clear_on_submit = False):
            # Main title displayed at the top of the survey page.
            display_intro()

            # Display the feedback button
            display_feedback_button()

            st.write(_("This is your respone no."), st.session_state.count)
            st.divider()

            st.write(current_fragment["Content"].encode("utf-16", "surrogatepass").decode("utf-16"))
            st.divider()

            # Define the options for the Human vs. Machine Generated Score
            human_machine_score_default = 0.5
            human_machine_score_options = {
                0.0: _("Definetly Human Generated"),
                0.2: _("Probalby Human Generated"),
                0.4: _("Likey Human Generated"),
                0.5: _("Choose an option"),  # Placeholder option
                0.6: _("Likey Machine Generated"),
                0.8: _("Probalby Machine Generated"),
                1.0: _("Definetly Machine Generated")
            }

            # Create the slider for the participant to rate whether they believe the news was generated by a human or machine
            human_machine_score = st.select_slider(
                label = _("Human or Machine Generated?"),
                options = list(human_machine_score_options.keys()),
                format_func = lambda x: human_machine_score_options[x],
                key = f"hm_score_{current_fragment['FragmentID']}",
                value = human_machine_score_default
            )

            # Define the options for the Legitimacy Score
            legit_fake_score_default = 0.5
            legit_fake_score_options = {
                0.0: _("Definetly Legit News"),
                0.2: _("Probalby Legit News"),
                0.4: _("Likey Legit News"),
                0.5: _("Choose an option"),  # Placeholder option
                0.6: _("Likey Fake News"),
                0.8: _("Probalby Fake News"),
                1.0: _("Definetly Fake News")
            }

            # Create the slider for the participant to rate the perceived legitimacy of the news
            legit_fake_score = st.select_slider(
                label = _("Legit or Fake News?"),
                options = list(legit_fake_score_options.keys()),
                format_func = lambda x: legit_fake_score_options[x],
                key = f"lf_score_{current_fragment['FragmentID']}",
                value = legit_fake_score_default
            )

            # Define the options for the knowledge about the topic
            topic_knowledge_score_default = 0.5
            topic_knowledge_score_options = {
                0.0: _("Not at all"),
                0.2: _("Slightly"),
                0.4: _("Somewhat"),
                0.5: _("Choose an option"),  # Placeholder option
                0.6: _("Fairly well"),
                0.8: _("Very well"),
                1.0: _("Extremely well")
            }

            # Create the slider for participants to rate their knowledge on the topic
            topic_knowledge_score = st.select_slider(
                label = _("How familiar are you with the topic covered in this news?"),
                options = list(topic_knowledge_score_options.keys()),
                format_func = lambda x: topic_knowledge_score_options[x],
                key = f"topic_knowledge_{current_fragment['FragmentID']}",
                value = topic_knowledge_score_default
            )

            st.divider()

            # Display results every 5 responses
            display_aggregate_results()

            # Display participant ID
            display_participant_id()

            # Submit button for each news fragment response.
            submitted = st.form_submit_button(_("Submit Response"))
            if submitted:
                validity = True
                # Validity checks
                if human_machine_score == human_machine_score_default:
                    st.error(_("Please confirm how you assess if this news is human or machine generated."))
                    validity = False
                if legit_fake_score == legit_fake_score_default:
                    st.error(_("Please confirm how you assess if this news is legit or fake."))
                    validity = False
                if topic_knowledge_score == topic_knowledge_score_default:
                    st.error(_("Please confirm how you assess your topic knowledge."))
                    validity = False
                if validity:
                    with st.spinner(_("Wait for it...")):
                        # Calculate the time taken to answer this fragment.
                        end_time = datetime.now()
                        time_to_answer = (end_time - st.session_state.start_time).total_seconds()

                        # Save the response to the database and session state.
                        save_response(current_fragment["FragmentID"], human_machine_score, legit_fake_score, topic_knowledge_score, time_to_answer, current_fragment["Origin"], current_fragment["IsFake"])
                        
                        # Increment the fragment index and response count for the session.
                        st.session_state.current_fragment_index = (st.session_state.current_fragment_index + 1) % len(st.session_state.fragments)
                        st.session_state.count = st.session_state.count + 1

                        # Reset the start time for the next fragment's response timing.
                        st.session_state.start_time = datetime.now()
                    
                    st.success(_("Done!"))
                    st.rerun()
