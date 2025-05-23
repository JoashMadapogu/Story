# Data Storytelling Guide

An AI-powered assistant that transforms data analysis results into compelling, context-aware narratives using a self-critique loop for continuous refinement.

## Overview

The Data Storytelling Guide is designed to help users create engaging stories from their data. It:

1. Takes an input data source and target audience
2. Generates an initial structured story
3. Uses a self-critique loop to iteratively refine the story
4. Delivers a polished final output

## Features

- **Automated Storytelling**: Generates clear narratives from data inputs
- **Self-Critique**: Uses an AI-powered loop to evaluate and improve the story
- **Audience Targeting**: Tailors the narrative to specific audiences
- **Structured Output**: Creates well-organized stories with clear sections
- **Data Processing**: Supports multiple data formats:
  - Images (.png, .jpg)
  - Documents (.pdf)
  - CSV files
  - Tableau dashboards (.twb, .twbx)
  - Power BI exports (.pbix)
- **User Preferences**: Learns and applies user preferences for:
  - Writing tone (formal, casual, technical, persuasive, balanced)
  - Output format (standard, executive, detailed, bullet)
  - Focus areas (key trends, outliers, actionable insights)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd data-storytelling-guide
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the Google ADK (Agent Development Kit):
   - Follow the [official guide](https://google.github.io/adk-docs/get-started/quickstart/)
   - Install the ADK package
   - Set up authentication

5. Set your API keys and authentication:
```bash
export GOOGLE_API_KEY=your_api_key_here
```

## Usage

### Basic Usage

Run the Data Storytelling Guide with a data source and target audience:

```bash
python main.py --data_source "path/to/data.csv" --audience "executive team"
```

### Advanced Usage

Specify output file and user preferences:

```bash
python main.py \
  --data_source "Q1 Sales Dashboard" \
  --audience "marketing team" \
  --output "sales_story.txt" \
  --tone "persuasive" \
  --format "executive" \
  --focus "key_trends,outliers,recommendations" \
  --save_preferences
```

### Parameters

- `--data_source`: Path to data file or description of data source (required)
- `--audience`: Target audience for the story (required)
- `--output`: Output file path (optional)
- `--user_id`: User ID for preferences (optional, defaults to "user_01")
- `--tone`: Story tone (formal, casual, technical, persuasive, balanced)
- `--format`: Story format (standard, executive, detailed, bullet)
- `--focus`: Comma-separated list of focus areas
- `--save_preferences`: Save current preferences for future use

## Example

```bash
python main.py \
  --data_source "Monthly Revenue Chart.png" \
  --audience "board members" \
  --tone "formal" \
  --format "executive"
```

This will generate a formal, executive-style story suitable for board members based on the revenue chart.

## Advanced Features

- **Section Regeneration**: The agent can regenerate specific sections of the story while preserving others
- **Iterative Refinement**: The story improves through multiple rounds of self-critique
- **Completion Detection**: Automatically detects when the story reaches satisfactory quality
- **Data Analysis**: Basic statistical analysis for CSV files
- **Image Processing**: Basic image analysis for visualization files
- **PDF Processing**: Text extraction and analysis for PDF documents

## Development

### Project Structure

```
data-storytelling-guide/
├── agent.py           # Main agent implementation
├── main.py           # Command-line interface
├── data_processor.py # Data format handling
├── preferences.py    # User preference management
├── requirements.txt  # Dependencies
└── README.md         # Documentation
```

### Adding New Features

1. Data Format Support:
   - Add new format handlers in `data_processor.py`
   - Update the `_process_file` method

2. User Preferences:
   - Add new preference types in `preferences.py`
   - Update the validation logic

3. Story Generation:
   - Modify agent instructions in `agent.py`
   - Add new tools as needed

## Future Development

- Support for more data formats
- Enhanced user preference learning
- Direct integration with visualization tools
- Voice output options
- Multi-language support
- Real-time collaboration features 