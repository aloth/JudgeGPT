import streamlit as st
import pandas as pd
import uuid
import json
import codecs
import base64
import urllib.request
import urllib.parse
import gettext
from typing import Dict, List, Optional, Union
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import errors as pymongo_errors
from streamlit_javascript import st_javascript

__name__ = "JudgeGPT"
__version__ = "1.1.0"
__author__ = "Alexander Loth"
__email__ = "alexander.loth@stud.fra-uas.de"
__research_paper__ = "https://arxiv.org/abs/2404.03021"
__report_a_bug__ = "https://github.com/aloth/JudgeGPT/issues"

def save_participant(language, age, gender, political_view, is_native_speaker, education_level, newspaper_subscription, fnews_experience, screen_resolution, ip_location, user_agent, query_params):
    """
    Save participant details to session state and MongoDB for persistence.

    Args:
        language (str): Participant's ISO language code.
        age (int): Participant's age.
        gender (str): Participant's gender.
        political_view (str): Participant's political view.
        is_native_speaker (bool): Whether the participant is a native speaker.
        education_level (str): Participant's education level.
        newspaper_subscription (bool): Whether the participant has a newspaper subscription.
        fnews_experience (str): Experience with fake news.
        screen_resolution (str): Screen resolution of the participant's device.
        ip_location (str): IP-based location of the participant.
        user_agent (str): Browser user agent string.
        query_params (dict): Additional query parameters from the request.
    
    Returns:
        bool: True if saving was successful, False otherwise.
    """
    # Create a participant dictionary to store user details.
    participant = {
        "ParticipantID": st.session_state.user_id,  # Unique user ID from session state.
        "ISOLanguage": language,
        "Age": age,
        "Gender": gender,
        "PoliticalView": political_view,
        "IsNativeSpeaker": is_native_speaker,
        "EducationLevel": education_level,
        "NewspaperSubscription": newspaper_subscription,
        "FNewsExperience": fnews_experience,  # Experience related to fake news.
        "ScreenResolution": screen_resolution,
        "IpLocation": ip_location,
        "UserAgent": user_agent,
        "QueryParams": query_params  # Optional query params, if any.
    }

    try:
        # Connect to MongoDB and insert participant data.
        with MongoClient(st.secrets["mongo"].connection, server_api=ServerApi('1')) as client:
            db = client.realorfake  # Access 'realorfake' database.
            collection = db.participants  # Access 'participants' collection.
            collection.insert_one(participant)  # Insert participant record.

        # Update session state with participant data for local session tracking.
        st.session_state.participant = participant
        return True
    except pymongo_errors.PyMongoError as e:
        st.error(_("Database error: Could not save participant data. Please try again later."))
        print(f"MongoDB Error during participant save: {e}")
        return False

def save_response(fragment_id, human_machine_score, legit_fake_score, topic_knowledge_score, time_to_answer, origin, is_fake, reported_as_broken):
    """
    Save survey response data to session state and MongoDB.

    Args:
        fragment_id (str): ID of the fragment the participant is responding to.
        human_machine_score (float): Participant's score on whether the fragment is machine-generated.
        legit_fake_score (float): Score on how legitimate or fake the fragment is perceived to be.
        topic_knowledge_score (float): Score on participant's knowledge of the topic.
        time_to_answer (float): Time taken to respond, in seconds.
        origin (str): Source or origin of the news fragment.
        is_fake (bool): Whether the fragment is actually fake.
        reported_as_broken (bool): Whether the fragment was flagged as broken by the user.
    
    Returns:
        bool: True if saving was successful, False otherwise.
    """
    # Create a response dictionary to store survey response details.
    response = {
        "ResultID": uuid.uuid4().hex,  # Unique response ID.
        "ParticipantID": st.session_state.user_id,  # Link to participant's ID.
        "FragmentID": fragment_id,  # ID of the evaluated fragment.
        "HumanMachineScore": human_machine_score,  # Perception of whether it’s human- or machine-generated.
        "LegitFakeScore": legit_fake_score,  # Legitimacy score.
        "TopicKnowledgeScore": topic_knowledge_score,  # Participant's self-rated topic knowledge.
        "Timestamp": datetime.now().isoformat(),  # Current timestamp for when the response is recorded.
        "TimeToAnswer": time_to_answer,  # Time spent answering.
        "SessionCount": st.session_state.count,  # Count of how many fragments the participant has reviewed in this session.
        "Origin": origin,  # Source of the fragment (e.g., news outlet, user-generated).
        "IsFake": is_fake,  # Ground truth on whether the fragment is fake.
        "ReportedAsBroken": reported_as_broken  # Whether the user flagged the fragment as problematic.
    }
    
    try:
        # Connect to MongoDB and insert response data.
        with MongoClient(st.secrets["mongo"].connection, server_api=ServerApi('1')) as client:
            db = client.realorfake  # Access 'realorfake' database.
            collection = db.results  # Access 'results' collection.
            collection.insert_one(response)  # Insert response record.
        
        # Append the new response to session state to track locally.
        st.session_state.responses.append(response)
        return True
    except pymongo_errors.PyMongoError as e:
        st.error(_("Database error: Could not save your response. Please try again."))
        print(f"MongoDB Error during response save: {e}")
        return False

def retrieve_fragments(ISOLanguage):
    """
    Retrieves a set of news fragments from MongoDB based on the participant's language preference.

    Args:
        ISOLanguage (str): The ISO language code for the desired fragments.

    Returns:
        List[Dict[str, Union[str, bool]]]: A list of dictionaries containing fragment data.
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
                    "MachineModel": 1,
                    "_id": 0
                    }},  # Project only required attributes
                {"$sample": {"size": 50}}
            ]
            fragments = collection.aggregate(pipeline)
            st.toast(_("Data retrieved."))
            return list(fragments)


def retrieve_fragments_by_ids(fragment_ids):
    """
    Retrieves specific fragments by their IDs (for challenge mode).

    Args:
        fragment_ids (list): List of FragmentID strings.

    Returns:
        List[Dict]: Ordered list of fragment dicts matching the input IDs.
    """
    with st.spinner(_("Loading challenge...")):
        with MongoClient(st.secrets["mongo"].connection, server_api=ServerApi('1')) as client:
            db = client.realorfake
            collection = db.fragments
            pipeline = [
                {"$match": {"FragmentID": {"$in": fragment_ids}}},
                {"$project": {
                    "FragmentID": 1,
                    "Content": 1,
                    "Origin": 1,
                    "IsFake": 1,
                    "MachineModel": 1,
                    "_id": 0
                }}
            ]
            results = list(collection.aggregate(pipeline))
            # Preserve the original order from fragment_ids
            id_to_frag = {f["FragmentID"]: f for f in results}
            return [id_to_frag[fid] for fid in fragment_ids if fid in id_to_frag]


def encode_challenge(fragment_ids, creator_score=None):
    """
    Encode fragment IDs and optional creator score into a URL-safe challenge token.

    Args:
        fragment_ids (list): List of FragmentID hex strings.
        creator_score (float, optional): Creator's accuracy percentage.

    Returns:
        str: Base64url-encoded challenge token.
    """
    payload = {"f": fragment_ids}
    if creator_score is not None:
        payload["s"] = round(creator_score, 1)
    raw = json.dumps(payload, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_challenge(token):
    """
    Decode a challenge token back into fragment IDs and optional score.

    Args:
        token (str): Base64url-encoded challenge token.

    Returns:
        tuple: (fragment_ids: list, creator_score: float or None)
    """
    try:
        # Re-add padding
        padding = 4 - len(token) % 4
        if padding != 4:
            token += "=" * padding
        raw = base64.urlsafe_b64decode(token)
        payload = json.loads(raw)
        return payload.get("f", []), payload.get("s")
    except Exception:
        return [], None

def get_user_agent():
    """
    Retrieves the browser's user agent string using JavaScript.

    Returns:
        Optional[str]: The user agent string if available, None otherwise.
    """
    try:
        user_agent = st_javascript('navigator.userAgent')
        if user_agent: return user_agent
        else: return None
    except: return None

def get_screen_resolution():
    """
    Retrieves the device's screen resolution using JavaScript.

    Returns:
        Optional[Dict[str, int]]: A dictionary containing 'width' and 'height' if available, None otherwise.
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

    Returns:
        Optional[Dict[str, str]]: A dictionary containing IP location information if available, None otherwise.
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

def get_announcement_messages():
    """
    Returns a dictionary of announcement messages keyed by message ID.
    Add new messages here with incrementing IDs.

    Returns:
        Dict[int, str]: A dictionary mapping message IDs to HTML content.
    """
    messages = {
        1: f"""
        <div style="
            background-color: #eef7ff;
            border-left: 5px solid #0072b2;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        ">
            <h3 style="color: #0072b2; margin-top: 0;">{_("Are you an expert in AI, policy, or journalism?")}</h3>
            <p style="margin-bottom: 1rem;">{_("We are conducting a follow-up study to gather expert perspectives on the risks and mitigation strategies related to AI-driven disinformation. Your insights are invaluable for this research.")}</p>
            <p style="margin-bottom: 1rem;">{_("Please consider contributing by participating in our 15-minute survey:")}</p>
            <p>➡️ <strong><a href="https://forms.gle/EUdbkEtZpEuPbVVz5" target="_blank" rel="noopener noreferrer">{_("Click here to access the Expert Survey")}</a></strong></p>
        </div>
        """,
        # Add more messages here as needed:
        # 2: """<div>...</div>""",
        # 3: """<div>...</div>""",
    }
    return messages

def display_intro():
    """
    Displays main title and intro.

    Returns:
        None
    """
    st.subheader("🔍 " + _("Real or Fake: Can You Spot Misinformation?"))
    st.markdown(_("**Challenge your ability to distinguish between authentic news and AI-generated fake news in our interactive quiz.**"))
    st.markdown(_("Dive into the complex world where generative AI blurs the lines between reality and fiction. Learn more about the impact of Generative AI on fake news through our [open access paper](https://arxiv.org/abs/2404.03021) and explore our research at [Cyber CNI](https://cybercni.fr/research/lutte-informatique-dinfluence-l2i-fake-news-detection-generation-prevention/)."))

    # Get the 'msg' URL parameter (default: 1, which shows the expert survey box)
    # msg=0 hides all announcements, msg=1 shows message 1, msg=2 shows message 2, etc.
    msg_param = st.query_params.get("msg", "1")
    try:
        msg_id = int(msg_param)
    except (ValueError, TypeError):
        msg_id = 1  # Default to showing message 1 if invalid

    # Display the announcement message if msg_id > 0 and message exists
    if msg_id > 0:
        messages = get_announcement_messages()
        if msg_id in messages:
            st.markdown(messages[msg_id], unsafe_allow_html=True)
    
    with st.expander(_("FAQs & Useful Info"), expanded=False):
        st.markdown(_("- **Privacy Concerns?** Email us at alexander.loth@stud.fra-uas.de with your participant ID to request data deletion within one year of submission. Use 'Delete Request' as your subject line."))
        st.markdown(_("- **No Downloads Needed:** Access the quiz directly from your browser."))
        st.markdown(_("- **Experiencing Delays?** High traffic might slow down the website. Try revisiting later."))
        st.markdown(_("- **AI-Generated Content:** Some headlines are crafted by AI, potentially carrying biases based on the data they were trained on."))

def display_participant_id():
    """
    Displays participant ID.

    Returns:
        None
    """
    st.markdown(
        '<p style="font-size: 12px;">' + _("Your participant ID:") + " " + st.session_state.user_id + '</p>',
        unsafe_allow_html=True
    )

def display_consent_box():
    """
    Display consent information.

    Returns:
        None
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

    Args:
        url (str): The URL to fetch content from.

    Returns:
        Optional[str]: The decoded content if successful, None otherwise.
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

    Args:
        file_en (str): The filename for the English version.
        file_int (Optional[str]): The filename for internationalized versions, if applicable.

    Returns:
        None
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

    Returns:
        Dict[str, Union[int, float]]: A dictionary containing aggregated results.
    """
    if not st.session_state.responses:
        return "No responses found."

    # Convert the responses to a DataFrame for easy manipulation
    df = pd.DataFrame(st.session_state.responses)

    # Calculate averages
    avg_hm_score = df['HumanMachineScore'].mean()
    avg_lf_score = df['LegitFakeScore'].mean()
    avg_topic_knowledge = df['TopicKnowledgeScore'].mean()

    # Calculate HM_Accuracy
    predicted_machine = df['HumanMachineScore'] >= 0.5
    actual_machine = df['Origin'] == "Machine"
    df['HM_Accuracy'] = (predicted_machine == actual_machine).astype(int)
    
    # Calculate LF_Accuracy
    predicted_fake = df['LegitFakeScore'] >= 0.5
    # df['IsFake'] is already boolean
    df['LF_Accuracy'] = (predicted_fake == df['IsFake']).astype(int)
    
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
    Displays results from session state with shareable score card and social buttons.

    Returns:
        None
    """
    completed_response_count = st.session_state.count - 1
    if completed_response_count % 5 == 0 and completed_response_count != 0:
        results = aggregate_results()
        st.balloons()
        st.write("🎉 " + _("Congratulations! You've completed {completed_responses} responses. Here are your results so far:").format(completed_responses=results['Total Responses']))
        st.write("🤖 " + _("Human/Machine Accuracy:") + f" {results['Human/Machine Accuracy'] * 100:.0f}%")
        st.write("🤔 " + _("Legitimacy Accuracy:") + f" {results['Legitimacy Accuracy'] * 100:.0f}%")

        # --- Shareable Score Card ---
        hm_pct = int(results['Human/Machine Accuracy'] * 100)
        lf_pct = int(results['Legitimacy Accuracy'] * 100)
        avg_pct = int((hm_pct + lf_pct) / 2)
        total = results['Total Responses']

        # Visual score card (text-based grid, Wordle-style)
        def accuracy_bar(pct):
            filled = round(pct / 10)
            return "🟩" * filled + "⬜" * (10 - filled)

        score_card_text = (
            f"🔍 JudgeGPT — Can You Spot AI Fakes?\n\n"
            f"🤖 AI Detection:  {accuracy_bar(hm_pct)} {hm_pct}%\n"
            f"📰 Fake News:     {accuracy_bar(lf_pct)} {lf_pct}%\n"
            f"📊 {total} fragments evaluated\n\n"
            f"Can you beat my score? 👇\n"
        )

        # Display the visual score card
        st.code(score_card_text, language=None)

        # --- Social Share Buttons ---
        app_url = "https://judgegpt.streamlit.app/"

        # Build challenge link from the last 5 fragments
        if len(st.session_state.responses) >= 5:
            last_5_ids = [r["FragmentID"] for r in st.session_state.responses[-5:]]
            challenge_token = encode_challenge(last_5_ids, creator_score=avg_pct)
            challenge_url = f"{app_url}?challenge={challenge_token}"
        else:
            challenge_url = app_url

        share_text_encoded = urllib.parse.quote(
            f"I scored {avg_pct}% on JudgeGPT detecting AI-generated fake news! Can you beat me? 🤖📰"
        )
        challenge_url_encoded = urllib.parse.quote(challenge_url)

        x_url = f"https://twitter.com/intent/tweet?text={share_text_encoded}&url={challenge_url_encoded}"
        li_url = f"https://www.linkedin.com/sharing/share-offsite/?url={challenge_url_encoded}"
        wa_url = f"https://wa.me/?text={share_text_encoded}%20{challenge_url_encoded}"
        mail_subject = urllib.parse.quote("Can you beat my JudgeGPT score?")
        mail_body = urllib.parse.quote(f"I scored {avg_pct}% on JudgeGPT detecting AI-generated fake news!\n\nTry the same challenge: {challenge_url}")
        mail_url = f"mailto:?subject={mail_subject}&body={mail_body}"

        st.markdown(_("**Share your results and challenge your friends:**"))

        share_cols = st.columns(4)
        with share_cols[0]:
            st.markdown(f'<a href="{x_url}" target="_blank" style="text-decoration:none;font-size:1.4em;">𝕏 Share</a>', unsafe_allow_html=True)
        with share_cols[1]:
            st.markdown(f'<a href="{li_url}" target="_blank" style="text-decoration:none;font-size:1.4em;">💼 LinkedIn</a>', unsafe_allow_html=True)
        with share_cols[2]:
            st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;font-size:1.4em;">💬 WhatsApp</a>', unsafe_allow_html=True)
        with share_cols[3]:
            st.markdown(f'<a href="{mail_url}" style="text-decoration:none;font-size:1.4em;">📧 Email</a>', unsafe_allow_html=True)
        
        # Challenge link on its own line
        st.code(challenge_url, language=None)

        # --- Badges ---
        badge1, badge2 = st.columns(2)
        with badge1:
            if results['Human/Machine Accuracy'] >= 0.7:
                st.image("images/judgegpt_badge.jpg")
                st.write("🎖️ " + _("You've earned the JudgeGPT badge for achieving high accuracy in identifying Human/Machine generated content!") + " 🎉")
        
        with badge2:
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
    Initializes the translator with English as fallback.

    Args:
        lang (str): The ISO language code for translation. Defaults to "en".

    Returns:
        callable: A translation function.
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
    Checks if an available language is set in the URL query. 

    Args:
        query_params (Dict[str, List[str]]): The query parameters from the URL.
        allowed_languages (List[str]): A list of allowed language codes.

    Returns:
        Optional[str]: The language code if found and allowed, None otherwise.
    """
    try:
        language_param = query_params.get("language", [])

        # Check if the extracted language parameter is non-empty and if it is in allowed languages
        if language_param and language_param.lower() in allowed_languages:
            # Return the language code, converted to lower case for matching
            return language_param.lower()
        return None
    except Exception:
        return None
    
def display_feedback_button():
    """
    Displays a feedback button on the page.

    Returns:
        None
    """
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

# Get min and max age from URL query parameters.  Use .get and provide default as string
min_age_param = query_params.get("min_age", "16")  # string default
max_age_param = query_params.get("max_age", "133") # string default

# Convert the parameters to floats, using try-except for safety.
try:
    min_age = float(min_age_param)
except (ValueError, TypeError):
    min_age = 16.0  # Default value
try:
    max_age = float(max_age_param)
except (ValueError, TypeError):
    max_age = 133.0 # Default value

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
        age_default = (min_age + max_age) / 2 + .33
        age = st.slider(
            label = _("Age"),
            min_value = min_age,
            max_value = max_age,
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
                    success = save_participant(
                        language = language,
                        age = age,
                        gender = gender,
                        political_view = political_view,
                        is_native_speaker = is_native_speaker,
                        education_level = education_level,
                        newspaper_subscription = newspaper_subscription,
                        fnews_experience = fnews_experience,
                        screen_resolution = screen_resolution,
                        ip_location = ip_location,
                        user_agent = user_agent,
                        query_params = query_params
                    )
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
    if 'show_reveal' not in st.session_state:
        st.session_state.show_reveal = False
    if 'last_reveal' not in st.session_state:
        st.session_state.last_reveal = None
    if 'challenge_mode' not in st.session_state:
        st.session_state.challenge_mode = False
        st.session_state.challenge_creator_score = None
    if 'fragments' not in st.session_state:
        # Check for challenge mode
        challenge_token = st.query_params.get("challenge", None)
        if challenge_token:
            challenge_ids, creator_score = decode_challenge(challenge_token)
            if challenge_ids:
                st.session_state.fragments = retrieve_fragments_by_ids(challenge_ids)
                st.session_state.challenge_mode = True
                st.session_state.challenge_creator_score = creator_score
                if creator_score:
                    st.info(f"🎯 " + _("Challenge mode! Someone scored {score}% — can you beat them?").format(score=int(creator_score)))
        if 'fragments' not in st.session_state or not st.session_state.fragments:
            # Retrieve news fragments based on participant's language preference.
            st.session_state.fragments = retrieve_fragments(st.session_state.participant["ISOLanguage"])

    # Check if it's necessary to fetch more fragments and reset index if so.
    if st.session_state.current_fragment_index >= len(st.session_state.fragments):
        if st.session_state.challenge_mode:
            # Challenge complete — show comparison
            st.session_state.challenge_mode = False
        st.session_state.fragments = retrieve_fragments(st.session_state.participant["ISOLanguage"])  # Reload or fetch new data
        st.session_state.current_fragment_index = 0  # Reset index to start from the first fragment of the new set

    # --- Post-Response Reveal ---
    if st.session_state.show_reveal and st.session_state.last_reveal:
        reveal = st.session_state.last_reveal
        
        # Determine colors and icons
        origin_icon = "🤖" if reveal["origin"] == "Machine" else "✍️"
        fake_icon = "🚨" if reveal["is_fake"] else "✅"
        
        # Was the user correct?
        hm_correct = (reveal["user_hm"] >= 0.5) == (reveal["origin"] == "Machine")
        lf_correct = (reveal["user_lf"] >= 0.5) == reveal["is_fake"]
        
        reveal_container = st.container()
        with reveal_container:
            st.markdown("---")
            st.subheader("🔎 " + _("The Truth Behind the Last Fragment"))
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**{_('Source:')}** {origin_icon} **{reveal['origin']}**")
                if reveal["origin"] == "Machine" and reveal.get("model"):
                    # Format model name nicely: "openai_gpt-4.1" → "GPT-4.1 (OpenAI)"
                    parts = reveal["model"].split("_", 1)
                    if len(parts) == 2:
                        model_display = f"{parts[1].upper()} ({parts[0].capitalize()})"
                    else:
                        model_display = reveal["model"]
                    st.markdown(f"**{_('Model:')}** `{model_display}`")
                st.markdown(f"{'✅' if hm_correct else '❌'} " + _("Your guess: {guess}").format(
                    guess=_("Machine") if reveal["user_hm"] >= 0.5 else _("Human")))
            
            with col2:
                st.markdown(f"**{_('Veracity:')}** {fake_icon} **{'Fake' if reveal['is_fake'] else 'Legitimate'}**")
                st.markdown(f"{'✅' if lf_correct else '❌'} " + _("Your guess: {guess}").format(
                    guess=_("Fake") if reveal["user_lf"] >= 0.5 else _("Legitimate")))
            
            # Streak tracking
            if 'streak' not in st.session_state:
                st.session_state.streak = 0
                st.session_state.best_streak = 0
            
            if hm_correct and lf_correct:
                st.session_state.streak += 1
                st.session_state.best_streak = max(st.session_state.best_streak, st.session_state.streak)
                if st.session_state.streak >= 3:
                    st.markdown(f"🔥 " + _("Streak: {streak} correct in a row!").format(streak=st.session_state.streak))
            else:
                if st.session_state.streak >= 3:
                    st.markdown(f"💔 " + _("Streak broken at {streak}! Best: {best}").format(
                        streak=st.session_state.streak, best=st.session_state.best_streak))
                st.session_state.streak = 0

            st.markdown("---")
        
        # Button to continue to next fragment
        if st.button("➡️ " + _("Next Fragment"), type="primary"):
            st.session_state.show_reveal = False
            st.session_state.last_reveal = None
            st.rerun()
    
    # --- Main Fragment Display (only when not showing reveal) ---
    elif not st.session_state.show_reveal:
        current_fragment = st.session_state.fragments[st.session_state.current_fragment_index]
        with st.form(key=f"news_fragment_{current_fragment['FragmentID']}", clear_on_submit = False):
            # Main title displayed at the top of the survey page.
            display_intro()

            # Display the feedback button
            display_feedback_button()

            # Challenge mode indicator
            if st.session_state.challenge_mode:
                remaining = len(st.session_state.fragments) - st.session_state.current_fragment_index
                st.markdown(f"🎯 **{_('Challenge Mode')}** — {remaining} " + _("fragments remaining"))

            st.write(_("This is your respone no."), st.session_state.count)
            st.divider()

            st.write(current_fragment["Content"].encode("utf-16", "surrogatepass").decode("utf-16"))
            st.divider()

            # Define the options for the Human vs. Machine Generated Score
            human_machine_score_default = 0.5
            human_machine_score_options = {
                0.0: _("Definitely Human Generated"),
                0.2: _("Probably Human Generated"),
                0.4: _("Likely Human Generated"),
                0.5: _("Choose an option"),  # Placeholder option
                0.6: _("Likely Machine Generated"),
                0.8: _("Probably Machine Generated"),
                1.0: _("Definitely Machine Generated")
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
                0.0: _("Definitely Legit News"),
                0.2: _("Probably Legit News"),
                0.4: _("Likely Legit News"),
                0.5: _("Choose an option"),  # Placeholder option
                0.6: _("Likely Fake News"),
                0.8: _("Probably Fake News"),
                1.0: _("Definitely Fake News")
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

            # Add a checkbox to allow the user to report a news fragment as broken.
            reported_as_broken = st.checkbox(_("Flag this news fragment as technically incorrect or broken."))

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
                if not reported_as_broken:
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
                        success = save_response(
                            fragment_id = current_fragment["FragmentID"],
                            human_machine_score = human_machine_score,
                            legit_fake_score = legit_fake_score,
                            topic_knowledge_score = topic_knowledge_score,
                            time_to_answer = time_to_answer,
                            origin = current_fragment["Origin"],
                            is_fake = current_fragment["IsFake"],
                            reported_as_broken = reported_as_broken
                        )
                        
                        # Store reveal data for the post-response reveal screen
                        st.session_state.last_reveal = {
                            "origin": current_fragment["Origin"],
                            "is_fake": current_fragment["IsFake"],
                            "model": current_fragment.get("MachineModel"),
                            "user_hm": human_machine_score,
                            "user_lf": legit_fake_score,
                        }
                        st.session_state.show_reveal = True

                        # Increment the fragment index and response count for the session.
                        st.session_state.current_fragment_index = (st.session_state.current_fragment_index + 1) % len(st.session_state.fragments)
                        st.session_state.count = st.session_state.count + 1

                        # Reset the start time for the next fragment's response timing.
                        st.session_state.start_time = datetime.now()
                    
                    st.rerun()
