# JudgeGPT Data Dictionary

This document provides a comprehensive description of all three MongoDB collections used in the JudgeGPT research platform: `participants`, `results`, and `fragments`. Each attribute is explained with its data type, valid range, and meaning.

---

## Database Structure Overview

**Database Name:** `realorfake`

**Collections:**
1. **participants** - Stores demographic and psychographic data about study participants
2. **results** - Stores participant responses/judgments for each news fragment
3. **fragments** - Stores news content (both human-written and AI-generated)

---

## Collection 1: `participants`

Stores comprehensive demographic and psychographic information about each study participant collected during the initial survey form.

| Attribute | Data Type | Range/Values | Description |
|-----------|-----------|--------------|-------------|
| `_id` | ObjectId | MongoDB auto-generated | Unique document identifier (MongoDB internal) |
| `ParticipantID` | String (UUID hex) | 32-character hexadecimal | Unique identifier for each participant (generated via `uuid.uuid4().hex`) |
| `ISOLanguage` | String | `"en"`, `"fr"`, `"de"`, `"es"` | ISO language code for participant's preferred language:<br>• `"en"` = English<br>• `"fr"` = French<br>• `"de"` = German<br>• `"es"` = Spanish |
| `Age` | Float | Configurable (default: 16.0 - 133.0) | Participant's age in years. Range can be customized via URL query parameters (`?min_age=X&max_age=Y`) |
| `Gender` | String | `"Male"`, `"Female"`, `"Other"`, `"Prefer not to say"` | Participant's self-identified gender |
| `PoliticalView` | Float | 0.0 - 1.0 (7-point scale) | Participant's self-assessed political orientation on a normalized 0-1 scale:<br>• `0.0` = Far Left<br>• `0.2` = Left<br>• `0.4` = Center-Left<br>• `0.6` = Center-Right<br>• `0.8` = Right<br>• `1.0` = Far Right<br>• `0.5` is used as placeholder (not valid for submission) |
| `IsNativeSpeaker` | String | `"Yes"`, `"No"` | Whether the participant is a native speaker of the selected language |
| `EducationLevel` | String | `"None"`, `"High School"`, `"Apprenticeship"`, `"Bachelor's Degree"`, `"Master's Degree"`, `"Doctoral Degree"` | Highest level of education completed by the participant |
| `NewspaperSubscription` | Float | 0.0, 1.0, 2.0, 3.0 | Number of newspaper subscriptions the participant has:<br>• `0.0` = None<br>• `1.0` = One<br>• `2.0` = Two<br>• `3.0` = Three or more<br>• `1.5` is used as placeholder (not valid for submission) |
| `FNewsExperience` | Float | 0.0 - 1.0 (7-point scale) | Participant's self-assessed experience/familiarity with fake news:<br>• `0.0` = Completely unfamiliar<br>• `0.2` = Mostly unfamiliar<br>• `0.4` = Somewhat unfamiliar<br>• `0.6` = Somewhat familiar<br>• `0.8` = Mostly familiar<br>• `1.0` = Completely familiar<br>• `0.5` is used as placeholder (not valid for submission) |
| `ScreenResolution` | Object/Null | `{width: Number, height: Number}` | Participant's device screen resolution in pixels, collected via JavaScript:<br>• `width`: Screen width in pixels<br>• `height`: Screen height in pixels<br>• `null` if JavaScript fails to retrieve |
| `IpLocation` | Object/Null | IP geolocation data object | IP-based location information retrieved from freeipapi.com API. Contains fields like:<br>• `countryCode`: ISO country code<br>• `latitude`: Geographic latitude<br>• `longitude`: Geographic longitude<br>• Additional geolocation metadata<br>• `null` if API call fails |
| `UserAgent` | String/Null | Browser user agent string | Full browser user agent string collected via JavaScript (e.g., "Mozilla/5.0...")<br>• `null` if JavaScript fails to retrieve |
| `QueryParams` | Object | URL query parameters | Dictionary of all URL query parameters passed when participant accessed the survey (used for tracking campaign sources, A/B testing, etc.) |

---

## Collection 2: `results`

Stores individual participant responses/judgments for each news fragment they evaluate. This is the core collection containing all judgment data.

| Attribute | Data Type | Range/Values | Description |
|-----------|-----------|--------------|-------------|
| `_id` | ObjectId | MongoDB auto-generated | Unique document identifier (MongoDB internal) |
| `ResultID` | String (UUID hex) | 32-character hexadecimal | Unique identifier for each individual response/judgment (generated via `uuid.uuid4().hex`) |
| `ParticipantID` | String (UUID hex) | 32-character hexadecimal | Foreign key linking to the participant who made this judgment (matches `ParticipantID` in `participants` collection) |
| `FragmentID` | String (UUID hex) | 32-character hexadecimal | Foreign key linking to the news fragment being evaluated (matches `FragmentID` in `fragments` collection) |
| `HumanMachineScore` | Float | 0.0 - 1.0 (7-point scale) | Participant's judgment on whether content is human or machine-generated:<br>• `0.0` = Definitely Human Generated<br>• `0.2` = Probably Human Generated<br>• `0.4` = Likely Human Generated<br>• `0.6` = Likely Machine Generated<br>• `0.8` = Probably Machine Generated<br>• `1.0` = Definitely Machine Generated<br>**Lower values = more human-like perception** |
| `LegitFakeScore` | Float | 0.0 - 1.0 (7-point scale) | Participant's judgment on content legitimacy:<br>• `0.0` = Definitely Legit News<br>• `0.2` = Probably Legit News<br>• `0.4` = Likely Legit News<br>• `0.6` = Likely Fake News<br>• `0.8` = Probably Fake News<br>• `1.0` = Definitely Fake News<br>**Lower values = more legitimate perception** |
| `TopicKnowledgeScore` | Float | 0.0 - 1.0 (7-point scale) | Participant's self-assessed familiarity with the topic:<br>• `0.0` = Not at all familiar<br>• `0.2` = Slightly familiar<br>• `0.4` = Somewhat familiar<br>• `0.6` = Fairly well familiar<br>• `0.8` = Very well familiar<br>• `1.0` = Extremely well familiar |
| `Timestamp` | String (ISO 8601) | ISO format datetime string | Exact timestamp when the response was submitted (format: `"YYYY-MM-DDTHH:MM:SS.mmmmmm"`), generated via `datetime.now().isoformat()` |
| `TimeToAnswer` | Float | Positive number (seconds) | Time elapsed (in seconds) between when the fragment was displayed and when the participant submitted their response. Calculated as `(end_time - start_time).total_seconds()` |
| `SessionCount` | Integer | Positive integer (1, 2, 3, ...) | Sequential response number within the participant's current session (starts at 1, increments with each submitted response) |
| `Origin` | String | `"Human"`, `"Machine"` | Ground truth: Actual origin of the news fragment:<br>• `"Human"` = Written by a human journalist<br>• `"Machine"` = Generated by AI/LLM |
| `IsFake` | Boolean | `true`, `false` | Ground truth: Whether the content is actually fake news/misinformation:<br>• `true` = Content is fake/misinformation<br>• `false` = Content is legitimate news |
| `ReportedAsBroken` | Boolean | `true`, `false` | Whether the participant flagged this fragment as technically incorrect or broken:<br>• `true` = Participant reported an issue<br>• `false` = No issues reported<br>Fragments reported as broken bypass the validation requirements for scores |

### Score Interpretation Notes

**For Analysis:**
- **HumanMachineScore >= 0.5** suggests participant perceived content as machine-generated
- **HumanMachineScore < 0.5** suggests participant perceived content as human-generated
- **LegitFakeScore >= 0.5** suggests participant perceived content as fake
- **LegitFakeScore < 0.5** suggests participant perceived content as legitimate

**Accuracy Calculations (as implemented in `aggregate_results()`):**
- **HM_Accuracy**: `(HumanMachineScore >= 0.5) == (Origin == "Machine")`
- **LF_Accuracy**: `(LegitFakeScore >= 0.5) == IsFake`

---

## Collection 3: `fragments`

Stores news content fragments used in the study, including both human-written articles and AI-generated content.

| Attribute | Data Type | Range/Values | Description |
|-----------|-----------|--------------|-------------|
| `_id` | ObjectId | MongoDB auto-generated | Unique document identifier (MongoDB internal) |
| `FragmentID` | String (UUID hex) | 32-character hexadecimal | Unique identifier for each news fragment (generated via `uuid.uuid4().hex`) |
| `Content` | String | Text content | The actual news fragment text that participants evaluate. Can be:<br>• Human-written news excerpt from real outlets<br>• AI-generated content from LLMs<br>Typically 1-3 paragraphs in length |
| `Origin` | String | `"Human"`, `"Machine"` | Source type of the content:<br>• `"Human"` = Written by human journalist<br>• `"Machine"` = Generated by AI/LLM |
| `ISOLanguage` | String | `"en"`, `"fr"`, `"de"`, `"es"` | ISO language code of the content:<br>• `"en"` = English<br>• `"fr"` = French<br>• `"de"` = German<br>• `"es"` = Spanish |
| `IsFake` | Boolean | `true`, `false` | Whether the content constitutes fake news/misinformation:<br>• `true` = Fake news/misinformation<br>• `false` = Legitimate news |
| `CreationDate` | Date/DateTime | ISO datetime | Date when the fragment was created/ingested into the database |
| `HumanOutlet` | String | Outlet name or empty string | **Only for Origin="Human"**: Name of the news outlet/publication source (e.g., "New York Times", "BBC")<br>• Empty string `""` if Origin="Machine" |
| `HumanURL` | String | URL or empty string | **Only for Origin="Human"**: Original URL of the source article<br>• Empty string `""` if Origin="Machine" |
| `MachineModel` | String | Model identifier or empty string | **Only for Origin="Machine"**: Identifier of the LLM used to generate the content. Examples:<br>• `"openai_gpt-4"`<br>• `"openai_gpt-35-turbo"`<br>• `"openai_gpt-4o_2024-08-06"`<br>• `"meta_llama-2-13b-chat"`<br>• `"google_gemma-7b-it"`<br>• `"mistralai_mistral-7b-instruct-v0.2"`<br>• `"microsoft_Phi-3-mini-4k-instruct"`<br>• Empty string `""` if Origin="Human" |
| `MachinePrompt` | String | Prompt text or empty string | **Only for Origin="Machine"**: The exact prompt used to generate the content (e.g., "Write a tweet about '''climate change''' in English in the style of CNN")<br>• Empty string `""` if Origin="Human" |
| **[Dynamic Keys]** | Various | Varies by fragment | Additional metadata fields from RogueGPT's prompt template components (e.g., `"Format"`, `"SeedPhrase"`, `"Language"`, `"Style"`) are stored dynamically based on the generation configuration |

### Fragment Query Pattern

When retrieving fragments for a participant, the system uses:
```javascript
{
  "$match": {"ISOLanguage": <participant_language>},
  "$project": {"FragmentID": 1, "Content": 1, "Origin": 1, "IsFake": 1, "_id": 0},
  "$sample": {"size": 50}
}
```
This randomly selects 50 fragments in the participant's chosen language.

---

## Data Collection Flow

1. **Participant Registration:**
   - User fills out demographic form
   - Record inserted into `participants` collection
   - `ParticipantID` generated and stored in session

2. **Fragment Retrieval:**
   - System queries `fragments` collection based on `ISOLanguage`
   - 50 random fragments loaded for the session

3. **Judgment Collection:**
   - For each fragment, participant provides three scores
   - `TimeToAnswer` calculated from presentation to submission
   - Record inserted into `results` collection with:
     - Link to `ParticipantID`
     - Link to `FragmentID`
     - All judgment scores
     - Ground truth (`Origin` and `IsFake`)

4. **Feedback Loop:**
   - Every 5 responses, system calculates accuracy metrics
   - Aggregation performed on session's `results` data
   - No database writes for feedback calculations

---

## Data Validation Rules

### Participants Collection
- All demographic fields must be selected (cannot remain at placeholder values)
- `PoliticalView`, `NewspaperSubscription`, and `FNewsExperience` cannot be `0.5` or `1.5` (placeholder values)
- Consent toggle must be `true`
- `Age` must be within configured min/max range

### Results Collection
- If `ReportedAsBroken = false`, all three scores must be selected (cannot remain at `0.5`)
- If `ReportedAsBroken = true`, validation is bypassed
- `TimeToAnswer` must be positive
- `ParticipantID` and `FragmentID` must reference existing documents

### Fragments Collection
- `Content` cannot be empty
- `Origin` must be either `"Human"` or `"Machine"`
- If `Origin = "Human"`: `HumanOutlet` and `HumanURL` should be populated, `MachineModel` and `MachinePrompt` should be empty
- If `Origin = "Machine"`: `MachineModel` and `MachinePrompt` should be populated, `HumanOutlet` and `HumanURL` should be empty

---

## Usage for Analysis

### Merging Collections

To analyze the full dataset, merge the three collections:

```python
# Merge results with fragments
df_merged = df_results.merge(df_fragments, on="FragmentID", suffixes=("_result", "_fragment"))

# Merge with participants
df_merged = df_merged.merge(df_participants, on="ParticipantID", suffixes=("", "_participant"))
```

### Key Analysis Variables

- **Demographic Predictors:** `Age`, `Gender`, `PoliticalView`, `EducationLevel`, `FNewsExperience`
- **Judgment Accuracy:** Compare participant scores to ground truth (`Origin`, `IsFake`)
- **Model Performance:** Group by `MachineModel` to compare which LLMs fool participants most effectively
- **Temporal Effects:** Use `SessionCount` and `TimeToAnswer` to detect fatigue or learning effects
- **Cross-Cultural:** Compare judgment patterns across `ISOLanguage` groups

---

## Data Privacy & Ethics

- **ParticipantID** is a randomly generated UUID with no personally identifiable information
- **IP geolocation** is approximate (city/country level) and collected via third-party API
- **User agent and screen resolution** are technical metadata, not personal identifiers
- All data collection follows informed consent procedures (consent toggle required)
- Participants can flag problematic fragments via `ReportedAsBroken`

---

## Version Information

- **Platform:** JudgeGPT v1.0.2
- **Generator:** RogueGPT v0.9.3
- **Database:** MongoDB (realorfake)
- **Last Updated:** October 2025
