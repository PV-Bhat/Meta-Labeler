# Meta-Labeler: Streamlined Conversation Labeling Tool

<div align="center">
  <img src="https://github.com/PV-Bhat/Meta-Labeler/blob/main/labelerGIF.gif" title="Labeling Workflow in Action" width="682" height="362">
</div>

Meta-labeler is a powerful, user-friendly tool for processing and labeling conversational data for analytics and optimization. Designed for precision and ease of use, it integrates seamlessly into workflows, enabling users to extract insights and streamline lead management. With features like dynamic segmentation control, customizable metrics, and real-time progress tracking, Meta-labeler simplifies conversation analysis for actionable outcomes.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Setup](#setup)
  - [Input Files](#input-files)
  - [Using LW Chrome Extension with Meta-Labeller](#using-lw-chrome-extension-with-meta-labeller)
- [Usage Instructions](#usage-instructions)
  - [Interface Overview](#interface-overview)
- [Scoring Mechanisms](#scoring-mechanisms)
- [Example Data](#example-data)
- [Applications and Benefits](#applications-and-benefits)
- [Contributions](#contributions)
- [License](#license)

## Features

- **Segmented Labeling:** Classify conversations across sales funnel stages:
  - **Intake:** Initial interactions with leads.
  - **Engaged:** Active interactions and follow-ups.
  - **Qualified:** Leads ready to proceed further.
- **Customizable Metrics:**
  - Sentiment Score (1: Very Negative to 5: Very Positive).
  - Engagement Score (1: Minimal to 5: Very High).
  - Customer Effort Score (1: Very Low to 5: Very High).
  - Response Type (Manual, Templated, GPT).
- **Color-Coded Segmentation:** Differentiate stages visually with unique colors.
- **Dynamic Segmentation Control:** Choose labeling modes (e.g., Intake Only), and the tool greys out irrelevant segments.
- **Data Export:** Automatically save labeled data into a structured Excel file (`labeled_conversations.xlsx`).

## Prerequisites

- **Python Version:** 3.8 or higher.
- **Dependencies:** Install the required libraries:
  ```bash
  pip install pandas openpyxl
  ```

## Getting Started

### Extract and Import data
- Use a data extraction tool like [LW-Chrome-Extension](https://github.com/PV-Bhat/LW-Chrome-Extension) to get JSON files with the conversations to be labeled.

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/meta-labeler.git
   cd meta-labeler
   ```
2. Place your JSON files in a folder named `conversations` in the same directory.
3. Run the tool from a terminal (Shift + Right-click and choose PowerShell):
   ```bash
   python conversation-labeler.py
   ```
4. Input the file directory in the shell in order to start labelling.

_Alternatively, you can also manually change the directory at:_

   ```python
   json_path = Path(r"C:\Users\REPLACE-YOUR-FOLDER-HERE\conversations")
   ```
### Input Files

Place JSON conversation files in the `conversations` folder. Example structure:
```json
{
  "conversation_data": [
    {"timestamp": "DD MMM YYYY, 16:48", "sender": "Lead name", "message": "Hi", "is_automated": false},
    {"timestamp": "DD MMM YYYY, 13:32", "sender": "Responder name", "message": "Hi there Thanks for getting in touch", "is_automated": false}
  ],
  "parsed_at": "...",
  "total_messages": 2
}
```

## Usage Instructions

### Interface Overview

1. **Select Segments to Label:**
     
   ![image](https://github.com/user-attachments/assets/62b27d46-0057-4898-90c5-25fc2c87ef4c)
     
   - Use the radio buttons under Segmentation Control to select the labeling mode.
   - Non-selected segments are disabled and greyed out.

2. **Label Data:**
     
   ![image](https://github.com/user-attachments/assets/431dc140-8689-49c4-8b23-6e38f53c97d9)
     
   - Assign metrics like Sentiment Score, Engagement Score, Customer Effort Score, and Response Type.

4. **Export Data:**
   Labeled data is saved automatically to `labeled_conversations.xlsx`.

## Scoring Mechanisms

- **Sentiment Score:** Rates the tone of the lead's messages (1 = Very Negative, 5 = Very Positive).
- **Engagement Score:** Measures interaction depth (1 = Minimal, 5 = Very High).
- **Customer Effort Score:** Assesses interaction difficulty (1 = Very Low Effort, 5 = Very High Effort).
- **Response Type:** Classifies responses as Manual, Templated, or GPT-generated.

## Example Data

The repository includes two sample JSON files in the `example-conversations` folder:
- `conversation_1.json`
- `conversation_2.json`

## Using LW Chrome Extension with Meta-Labeler

Follow instructions in README to download Meta-Labeler: https://github.com/PV-Bhat/Meta-Labeler

### Workflow
1. **Start with LW Chrome Extension**: Export conversations from Meta Business Suite into JSON format.
2. **Import into Meta-Labeller**: Use the exported JSON files as input for labeling.
3. **Analyze and Refine**: Label, analyze, and export the processed data to structured formats (e.g., Excel).

### Leads Wizard Ecosystem
Meta-Labeller, along with LW Chrome Extension, forms the foundation of the **[Leads Wizard](https://github.com/PV-Bhat/LeadsWizard)** ecosystem, designed to bring efficiency and insights to lead and customer management workflows.

## Applications and Benefits

Meta-labeler is ideal for:
- **Customer Support Teams:** Improving response quality and effort scores.
- **Sales Teams:** Streamlining lead qualification with data-driven insights.
- **Data Analysts:** Extracting actionable metrics from conversation data.

## Contributions

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch (`feature/your-feature-name`).
3. Commit your changes.
4. Push the branch and submit a Pull Request.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
