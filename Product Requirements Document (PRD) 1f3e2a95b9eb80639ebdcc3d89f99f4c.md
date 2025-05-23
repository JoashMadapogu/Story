# Product Requirements Document (PRD)

## Product Name: **Data Storytelling Guide**

## Author: Joash Madapogu

## Date: May 13th 2025

## Version: 1.1

## 1. Overview

### 1.1 Purpose

The **Data Storytelling Guide** is an AI-powered assistant that transforms raw or visual data analysis results (charts, Tableau dashboards, Power BI exports, PDF reports, etc.) into compelling, context-aware narratives. It enables users to communicate insights effectively by generating stories that are tailored to specific audiences, iteratively improved through self-critique, and personalized through learned preferences.

### 1.2 Scope

The system accepts various data formats and automatically extracts insights to generate text-based stories. It supports user feedback and iterative revision, and can remember user preferences for future storytelling tasks. The target users include analysts, consultants, educators, researchers, and professionals needing to explain data insights clearly.

## 2. Goals and Objectives

| Goal | Description |
| --- | --- |
| Automate storytelling | Auto-generate clear and insightful narratives from visual data |
| Support multiple formats | Accept images, Tableau, Power BI, and PDF input |
| Enable feedback-based refinement | Allow AI self-critique and user-requested improvements |
| Personalize output | Learn and apply user preferences (tone, format, focus) |

## 3. User Stories

### 3.1 Primary User Personas

- **Analyst Alice**: Wants to present key findings from Tableau charts to stakeholders.
- **Educator Emily**: Needs simple explanations of student data in PDF dashboards.
- **Consultant Carlos**: Prepares summary reports for client presentations.

### 3.2 Key User Stories

- *“As a data analyst, I want to upload my Power BI report and get a summary of key trends and recommendations.”*
- *“As a teacher, I want the AI to explain a chart to a non-technical audience.”*
- *“As a user, I want the AI to remember my preference for using a formal tone.”*
- *“As a researcher, I want to improve the story by giving suggestions and reviewing alternate versions.”*
- *“As a user, I want to tell the AI to regenerate only a specific section of the story or add/remove specific details from it.”*

## 4. Functional Requirements

### 4.1 Input Processing

Accept files: `.png`, `.jpg`, `.pdf`, `.twb/.twbx`, `.pbix`, `.csv`

Extract charts and tables from image and document files

Detect and parse graph types (bar, line, pie, scatter, etc.)

### 4.2 Insight Extraction

Identify trends, anomalies, correlations, and clusters

Summarize key statistical insights

Recognize chart titles, axis labels, and legends

### 4.3 Story Generation

Use LLM to generate:

- Title
- Introduction
- Key insights with narrative
- Conclusion or call-to-action

Allow output format selection: paragraph, bullet, executive summary, slide text

### 4.4 Self-Critique

Apply prompt chaining for self-review

Check for clarity, audience fit, redundancy, and coherence

Suggest improvements and alternative phrasings

### 4.5 User Interaction & Feedback

Let users accept, reject, or edit generated text

Support **re-generation of specific sections** (e.g., only the introduction or one insight)

Let users instruct the AI to **add, remove, or expand on specific parts** of the story

Allow users to give additional **data context or goals** (e.g., "Make it more persuasive", "Include more financial metrics")

Collect thumbs up/down and written feedback for model improvement

### 4.6 Preference Learning

Save tone preferences (e.g., formal, persuasive)

Save format choices (e.g., summary, storytelling)

Remember industry/role context if available

## 5. Non-Functional Requirements

| Category | Requirement |
| --- | --- |
| Performance | Output generated within 10 seconds for small files |
| Scalability | Support batch processing of up to 10 graphs per session |
| Security | Uploaded data is private and deleted after session |
| Usability | Simple drag-and-drop interface, clear interaction flow |
| Compatibility | Works across modern browsers and desktop environments |

## 6. System Architecture (Overview)

**Frontend:**

- Next.js or React UI
- File uploader, preview pane, story editor
- Login system (optional)

**Backend:**

- Node.js or Python (FastAPI)
- Integration with LangChain / Groq / OpenAI
- OCR & Graph Detection (OpenCV, Tesseract)
- Tableau/Power BI SDKs for native parsing

**Storage:**

- Redis: Session memory, feedback loop
- PostgreSQL or Firebase: User preferences & histories

**AI Models:**

- LLM: GPT-4 / Claude / Gemini
- Image Analysis: Custom graph parser or ML classifier
- Self-critique: Prompt chains using system role evaluation

## 7. Milestones & Timeline

| Phase | Description | Timeline |
| --- | --- | --- |
| Phase 1 | MVP with static image upload + basic story | Week 1 |
| Phase 2 | Add support for PDF, Tableau, Power BI | Week 1 |
| Phase 3 | Self-critique & feedback loop | Week 2 |
| Phase 4 | User preferences & personalization | Week 2 |
| Phase 5 | Beta launch & feedback collection | Week 2 |
| Phase 6 | Documentation & deployment | Week 2 |

## 8. Future Enhancements

- **Speech-to-Story:** Convert spoken presentation into critique-ready text
- **Voice Output:** Generate audio narration of the story
- **Plug-ins:** Direct integration into Tableau/Power BI/Google Slides

## 9. Example Flow

1. **Upload:** User uploads a Tableau dashboard export
2. **Extraction:** Key graphs and summary stats are parsed
3. **Draft Story:** LLM generates:
    - Intro (“What is this dashboard about?”)
    - Insights narrative
    - Conclusion or call to action
4. **Critique:** AI checks for audience clarity and narrative gaps
5. **User Feedback:** User edits or requests variations
6. **Final Output:** Download story as text, PDF, slide notes, or JSON

## 10. Success Metrics

- 85% of test users report increased clarity of their data story
- Average story generation and revision in <15 seconds
- 75% of users use feedback or preference features at least once
- Positive NPS from target user segments

## 11. Open Questions

- Should user authentication be required to save preferences?
- Should we support multi-lingual story generation?
- How to handle highly complex dashboards with over 10 visual elements?