# JudgeGPT: An Empirical Platform for Evaluating News Authenticity in the Age of AI
[![arXiv](https://img.shields.io/badge/arXiv-2404.03021-B31B1B.svg)](https://arxiv.org/abs/2404.03021)
[![arXiv](https://img.shields.io/badge/arXiv-2601.21963-B31B1B.svg)](https://arxiv.org/abs/2601.21963)
[![Participate in Survey](https://img.shields.io/badge/Participate-Survey-brightgreen.svg)](https://judgegpt.streamlit.app/)
[![React Beta Test](https://img.shields.io/badge/React%20Beta-Test-blue.svg)](https://aka.ms/JudgeGPT)
[![Status](https://img.shields.io/badge/status-active%20%26%20evolving-orange.svg)](https://github.com/aloth/JudgeGPT)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![GitHub Stars](https://img.shields.io/github/stars/aloth/JudgeGPT?style=social)](https://github.com/aloth/JudgeGPT/stargazers)

## The Research Mandate: Why JudgeGPT Exists
Generative AI has initiated a technological arms race between the creation of hyper-realistic synthetic media and the development of tools to detect it. While much research focuses on the technical aspects of automated detection, a critical gap exists in understanding human perception. How do people judge the authenticity of content when the lines between human and machine-generated text are increasingly blurred?

As identified in our foundational paper, *"Blessing or curse? A survey on the Impact of Generative AI on Fake News"*, there is a pressing need for empirical data to understand how these technologies influence public trust and information integrity. The paper highlights a "notable gap in the literature" concerning the dual-use nature of Generative AI and calls for research to explore both the technological and social countermeasures required to safeguard the information ecosystem.

Our follow-up research, *"Industrialized Deception: The Collateral Effects of LLM-Generated Misinformation on Digital Ecosystems"* (to appear at WWW '26), extends this work by examining the broader systemic impacts of LLM-generated misinformation on digital platforms, trust networks, and information ecosystems.

JudgeGPT is not just a survey; it is a live research platform designed to systematically collect and analyze human judgments on news authenticity. It serves as the practical instrument built to address this identified research gap, providing the crucial data needed to navigate this new information landscape.

## The Research Pipeline: From Generation to Judgment
To effectively study human perceptions of AI-generated news, a reliable and controllable source of stimuli is required. This project employs a two-part research apparatus, comprising the `JudgeGPT` and [`RogueGPT`](https://github.com/aloth/RogueGPT) repositories, which together form a complete, end-to-end experimental pipeline. This structure ensures methodological rigor by allowing for the systematic generation and evaluation of news content.

The relationship between these projects is not merely collaborative; it is a functional and structured research workflow. `RogueGPT` serves as the **stimulus generation engine**, creating content under controlled experimental conditions. `JudgeGPT` is the **data collection platform**, where human participants evaluate that content, providing the raw data for analysis.

### The Experimental Workflow
The process flows from controlled generation to human judgment, creating a rich dataset that links specific content characteristics to perception scores:

1.  **Controlled Stimulus Generation (`RogueGPT`):** A researcher utilizes the `RogueGPT` interface to generate news fragments. The generation process is highly controlled, using specific variables defined in a configuration file (`prompt_engine.json`). These variables include parameters such as news outlet `Style` (e.g., 'NYT', 'BILD'), `Format` ('tweet', 'short article'), `Language` ('en', 'de'), and the underlying `GeneratorModel` (e.g., 'openai_gpt-4-turbo_2024-04-09').

2.  **Data Storage (MongoDB):** Each generated fragment, along with its full metadata (the parameters used to create it), is stored in a shared MongoDB database. This is handled by the `save_fragment` function within `RogueGPT`'s codebase, which uses the PyMongo library to interact with the database.

3.  **Human Data Collection (`JudgeGPT`):** A participant accesses the `JudgeGPT` survey application. The application retrieves a fragment from the MongoDB collection to present to the user.

4.  **Judgment and Analysis:** The participant reads the news fragment and uses sliders to rate its perceived authenticity (Real vs. Fake) and origin (Human vs. Machine). This judgment data is then saved back to the database, creating a comprehensive record that links specific generation parameters to quantitative human perception scores. This closed-loop system allows for robust statistical analysis of the factors that influence the believability of AI-generated text.

## Getting Involved: A Guide for Everyone
Whether you are a curious individual, a fellow researcher, or a developer, there are many ways to engage with the JudgeGPT project. Find the path that's right for you below.

| **Audience** | **Primary Goal** | **Action** |
| :--- | :--- | :--- |
| **General Public** | Test your ability to spot AI-generated news and contribute to our dataset. | **[Participate in the Survey](https://judgegpt.streamlit.app/)** <br> **[Test the React Beta](https://aka.ms/JudgeGPT)** |
| **Researchers** | Understand, cite, or collaborate on this research. | **[Read the Paper](https://arxiv.org/abs/2404.03021)** <br> **[✉️ Contact Us](mailto:Alexander.Loth@microsoft.com)** <br> **[See Citation](#citation)** |
| **Developers** | Contribute code, fix bugs, or suggest features. | **[Fork the Repo](https://github.com/aloth/JudgeGPT/fork)** <br> **[🐞 Open an Issue](https://github.com/aloth/JudgeGPT/issues)** <br> **[See Contributing Guide](#contributing)** |

## 📢 Calling All Experts: Share Your Insights!
Are you an expert in AI, policy, or journalism? We are conducting a follow-up study to gather expert perspectives on the risks and mitigation strategies related to AI-driven disinformation. Your insights are invaluable for this research.

Please consider contributing by participating in our 15-minute survey:
**➡️ [https://forms.gle/EUdbkEtZpEuPbVVz5](https://forms.gle/EUdbkEtZpEuPbVVz5)**

* **Purpose**: This survey explores expert perceptions of generative-AI–driven disinformation for an academic research project.
* **Data Use**: All responses will be treated as confidential and reported in an anonymised, aggregated format by default. At the end of the survey, you will have the option to be publicly acknowledged for your contribution. All data will be used for academic purposes only.
* **Time**: Approximately 15 minutes.

## Technical Deep Dive
This section provides a comprehensive guide for developers and technical users who wish to run, inspect, or contribute to the JudgeGPT project locally.

### System Architecture
The project is built with the following components:

* **Frontend:** The primary interface is a **Streamlit** application, written in Python, designed for rapid prototyping and data interaction. An experimental port to **React** is in development for a more robust and scalable user experience.
* **Backend:** The application logic is written in **Python** and is contained within the main Streamlit script (`app.py`).
* **Database:** A **MongoDB** (NoSQL) database is used to store news fragments and user judgments. The dependency on `pymongo[srv]` suggests compatibility with cloud-hosted instances like MongoDB Atlas.

### Local Installation and Setup
Follow these steps to set up the project on your local machine.

1.  **Prerequisites**
    * Python 3.8+
    * pip package manager
    * Git

2.  **Clone the Repository**
    Open your terminal and run the following commands:
    ```bash
    git clone [https://github.com/aloth/JudgeGPT.git](https://github.com/aloth/JudgeGPT.git)
    cd JudgeGPT
    ```

3.  **Set Up a Virtual Environment (Recommended)**
    To maintain clean dependencies, it is highly recommended to use a virtual environment.
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

4.  **Install Dependencies**
    Install all required Python packages from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```
    Key dependencies include `streamlit`, `pymongo`, and `openai`.

5.  **Configure Environment Variables**
    The application requires a connection string to a MongoDB database. For local development, it is best practice to manage this secret using an environment variable rather than hardcoding it. You will need to set up a variable (e.g., `MONGO_CONNECTION_STRING`) with your database URI.

### Running the Application
Once the setup is complete, launch the Streamlit application with the following command:
```bash
streamlit run app.py
```
The application will open in your default web browser.

### Customization via URL Parameters
The survey experience can be customized by passing parameters in the URL.

* **Language Support:** JudgeGPT automatically detects the user's browser language but can be manually set. Supported languages are English (`en`), German (`de`), French (`fr`), and Spanish (`es`).
    * Example for German: `https://judgegpt.streamlit.app/?language=de`

* **Age Range:** You can filter participants by age using the `min_age` and `max_age` parameters.
    * Example for ages 15-25: `https://judgegpt.streamlit.app/?min_age=15&max_age=25`

## Data Analysis Tools

For researchers interested in analyzing the collected data, the [`data_analysis/`](data_analysis/) directory contains specialized tools for exporting and processing the MongoDB collections:

- **Data Export**: Export all study data (participants, results, fragments) to CSV and JSON formats
- **Automated Processing**: Timestamped exports with summary reports and ZIP archives
- **Research Ready**: Tools designed for independent use by researchers

See the [data_analysis README](data_analysis/README.md) for detailed usage instructions.

## Project Roadmap: A Research-Driven Agenda
JudgeGPT is an actively evolving research platform. The project roadmap is directly guided by the open challenges in the field of AI-driven misinformation, as outlined in our research paper. We welcome collaboration on the following key areas, which transform a list of features into a strategic agenda for advancing scientific understanding.

### Expanding Modalities: Beyond Text to Deepfakes
The current focus is on text-based news. However, the proliferation of "deepfakes" and other synthetic media presents a growing threat. The roadmap includes adding **image and video support**, allowing participants to evaluate the authenticity of visual content. This directly addresses the challenge of multimedia disinformation and expands the project's scope to cover the creation and detection of synthetic realities.

### Enhancing Realism and Deception
To keep pace with the "technological arms race," the research must test human perception against an ever-wider array of sophisticated models. This involves deeper integration with `RogueGPT`'s **cross-model generation** capabilities, incorporating outputs from models like BERT, T5, and other emerging LLMs. This will create a more challenging and ecologically valid testbed for human judgment.

### Building Trust and Mitigation Systems
The project aims to move beyond pure detection toward active mitigation. Future work includes building a **content verification layer** and integrating with established **fact-checking services**. This would allow the platform not only to identify potentially false content but also to provide users with corrective information, aligning with psychological "inoculation" strategies against misinformation.

### Globalizing the Research: Cross-Lingual and Cultural Analysis
True understanding of the fake news phenomenon requires a global perspective. The planned **expansion of localization and multilingual support** is not merely about translation. It is about enabling research into how the perception of AI-generated content differs across languages and cultural contexts, a significant and under-explored area of inquiry.

### Improving Engagement and Data Quality
To gather high-quality data at scale, participant engagement is key. The roadmap includes implementing **gamification elements** (scores, badges), an **interactive results dashboard**, and **personalized feedback mechanisms**. These features are designed not just for user enjoyment but to increase participant retention, motivation, and the overall volume and quality of the collected research data.

### Achieving Scalability and Production Readiness
To serve as a long-term, large-scale public resource, the platform must be robust and scalable. This involves transitioning to a **production-grade cloud environment** (e.g., Microsoft Azure) and making significant **UI/UX enhancements**, including the ongoing port to React. This ensures the platform's longevity and its ability to support a growing community of participants and researchers.

## Citation
If you use JudgeGPT or its underlying research in your work, please cite our paper:

```bibtex
@inproceedings{loth2026collateraleffects,
      author = {Loth, Alexander and Kappes, Martin and Pahl, Marc-Oliver},
      title = {Industrialized Deception: The Collateral Effects of LLM-Generated Misinformation on Digital Ecosystems},
      booktitle = {Companion Proceedings of the ACM Web Conference 2026 (WWW '26 Companion)},
      year = {2026},
      month = apr,
      publisher = {ACM},
      address = {New York, NY, USA},
      location = {Dubai, United Arab Emirates},
      url = {https://arxiv.org/abs/2601.21963},
      note = {To appear. Also available as arXiv:2601.21963}
}
```

## Contributing
We welcome contributions from the community! To get involved, please follow these steps:

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for full details.

## Acknowledgments
This work would not be possible without the foundational technologies and support from:
* OpenAI for their groundbreaking GPT models.
* Streamlit for enabling the rapid development of our web application.
* MongoDB for robust and scalable database solutions.
* The broader open-source community for providing invaluable tools and libraries.

## Disclaimer
JudgeGPT is an independent research project and is not affiliated with, endorsed by, or in any way officially connected to OpenAI. The use of "GPT" within the project name is employed in a *pars pro toto* manner, where it represents the broader class of Generative Pre-trained Transformer models and Large Language Models (LLMs) that are the subject of this research. The project's explorations and findings are its own and do not reflect the views or positions of OpenAI. We are committed to responsible AI research and adhere to ethical guidelines in all aspects of our work.
