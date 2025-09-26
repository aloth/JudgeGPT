# JudgeGPT Data Analysis Tools

This directory contains tools for analyzing and exporting data from the JudgeGPT research study. These tools are designed to be used independently by researchers.

## Overview

The JudgeGPT study collects data in three MongoDB collections:
- `participants`: Demographic and background information
- `results`: Participant responses to news fragment classification tasks
- `fragments`: News fragments used in the study

## export_data.py

A script that exports all MongoDB collections to CSV and JSON formats for offline analysis.

### Features

- Exports data to both CSV and JSON formats
- Timestamped files using `YYYYMMDDHHMMSS` format
- Creates ZIP archive containing all exported files
- Generates detailed summary report
- Handles MongoDB ObjectId conversion for compatibility

### Output Files

For each export run (example timestamp: `20250926135141`):
- `20250926135141-participants.csv` & `.json`
- `20250926135141-results.csv` & `.json`
- `20250926135141-fragments.csv` & `.json`
- `20250926135141-export_summary.txt`
- `20250926135141-judgegpt_export.zip`

## Setup

### Requirements
```bash
pip install pymongo pandas streamlit
```

### Database Configuration
The script uses the existing MongoDB connection from the main JudgeGPT application via `.streamlit/secrets.toml` in the parent directory.

Alternatively, set the environment variable:
```bash
$env:MONGODB_CONNECTION_STRING="your_connection_string"
```

## Usage

1. Navigate to the data_analysis directory
2. Run the export script:
   ```bash
   python export_data.py
   ```

All files are saved in the `data_dumps/` subdirectory.

## Data Structure

### Participants Collection
- `ParticipantID`, `ISOLanguage`, `Age`, `Gender`, `PoliticalView`
- `EducationLevel`, `NewspaperSubscription`, `IsNativeSpeaker`
- `FNewsExperience`, `ScreenResolution`, `IpLocation`, `UserAgent`

### Results Collection
- `ParticipantID`, `FragmentID`, `HumanMachineScore`, `LegitFakeScore`
- `TopicKnowledgeScore`, `TimeToAnswer`, `Origin`, `IsFake`

### Fragments Collection
- `FragmentID`, `Text`, `ISOLanguage`, `Origin`, `IsFake`, `Topic`

## Further Reading

- Research Paper: https://arxiv.org/abs/2404.03021