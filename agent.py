#!/usr/bin/env python3
# Data Storytelling Guide - Agent with Self-Critique Loop
# Follow https://google.github.io/adk-docs/get-started/quickstart/ for setup

from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools import ToolContext

# --- Constants ---
APP_NAME = "data_storytelling_guide"
USER_ID = "user_01"
SESSION_ID_BASE = "story_critique_session"
MODEL = "gemini-2.0-flash"

# --- State Keys ---
STATE_DATA_SOURCE = "data_source"
STATE_AUDIENCE = "audience"
STATE_USER_PREFERENCES = "user_preferences"
STATE_CURRENT_STORY = "current_story"
STATE_CRITICISM = "criticism"
STATE_FINAL_STORY = "final_story"
STATE_USER_FEEDBACK = "user_feedback"

# Define the exact phrase the Critic should use to signal completion
COMPLETION_PHRASE = "No significant improvements needed for this story."

# --- Tool Definition ---
def exit_loop(tool_context: ToolContext):
    """Call this function ONLY when the critique indicates no further changes are needed, 
    signaling the iterative process should end."""
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {}

def regenerate_section(tool_context: ToolContext, section_type, instruction):
    """Tool to regenerate only a specific section of the story.
    section_type: "introduction", "key_insights", "conclusion", etc.
    instruction: Specific guidance for regeneration."""
    print(f"  [Tool Call] regenerate_section triggered for {section_type}")
    current_story = tool_context.state.get(STATE_CURRENT_STORY, "")
    
    # Logic to handle section regeneration would be implemented here
    # For now, we'll just return the request for the main agent to handle
    return {
        "section_type": section_type,
        "instruction": instruction
    }

# --- Initial Story Generator Agent ---
story_generator_agent = LlmAgent(
    name="StoryGeneratorAgent",
    model=MODEL,
    include_contents='none',
    instruction="""You are a Data Storytelling Assistant that creates compelling narratives from data.

    Based on the data source, intended audience, and user preferences provided, craft a structured data story with:
    1. A clear title
    2. Introduction explaining context
    3. 3-4 key insights with supporting narrative
    4. Conclusion or call-to-action

    Data Source: {{data_source}}
    Target Audience: {{audience}}
    User Preferences: {{user_preferences}}

    Adapt your writing to match the preferred tone (formal, casual, technical, persuasive, or balanced) 
    and format (standard, executive, detailed, or bullet) from the user preferences.
    
    Focus on the areas specified in the user's focus_areas, if provided.

    Output ONLY the structured story with appropriate headings.
    """,
    description="Generates initial data story from provided data source, audience, and user preferences",
    output_key=STATE_CURRENT_STORY
)

# --- Critic Agent (Inside the Refinement Loop) ---
critic_agent = LlmAgent(
    name="CriticAgent",
    model=MODEL,
    include_contents='none',
    instruction=f"""You are a Data Story Reviewer evaluating a narrative created from data.

    **Data Story to Review:**
    ```
    {{current_story}}
    ```

    **Data Source:** {{data_source}}
    **Target Audience:** {{audience}}
    **User Preferences:** {{user_preferences}}

    **Task:**
    Review the story for:
    1. Clarity - Is the narrative easy to understand for the specified audience?
    2. Audience fit - Is the language and depth appropriate for the audience?
    3. Insight value - Does it highlight the most important patterns/trends?
    4. Coherence - Does the story flow logically?
    5. Completeness - Does it include all necessary sections?
    6. Preference alignment - Does it match the user's preferred tone, format, and focus areas?

    IF you identify 1-3 SPECIFIC ways the story could be improved:
    Provide actionable, detailed suggestions with examples. Focus on highest-value improvements.
    Pay special attention to ensuring the story aligns with the user's preferences.

    ELSE IF the story meets all requirements well:
    Respond EXACTLY with the phrase "{COMPLETION_PHRASE}" and nothing else.

    Output ONLY your critique OR the exact completion phrase.
    """,
    description="Reviews the current story draft against user preferences, providing specific critique or signaling completion",
    output_key=STATE_CRITICISM
)

# --- Refiner Agent (Inside the Refinement Loop) ---
refiner_agent = LlmAgent(
    name="RefinerAgent",
    model=MODEL,
    include_contents='none',
    instruction=f"""You are a Data Storytelling Assistant refining a story based on expert feedback.

    **Current Story:**
    ```
    {{current_story}}
    ```

    **Critique/Suggestions:**
    {{criticism}}

    **Task:**
    Analyze the critique carefully.
    
    IF the critique is EXACTLY "{COMPLETION_PHRASE}":
    You MUST call the 'exit_loop' function. Do not output any text.
    
    ELSE (the critique contains actionable feedback):
    Apply ALL the suggestions to improve the story. Maintain the same structure (title, introduction, insights, conclusion) but enhance the content based on the feedback.
    Output ONLY the refined story with all improvements integrated.
    """,
    description="Refines the story based on critique, or calls exit_loop if critique indicates completion",
    tools=[exit_loop, regenerate_section],
    output_key=STATE_CURRENT_STORY
)

# --- Refinement Loop Agent ---
refinement_loop = LoopAgent(
    name="RefinementLoop",
    sub_agents=[
        critic_agent,
        refiner_agent,
    ],
    max_iterations=5  # Limit loops for efficiency
)

# --- Final Output Agent ---
final_output_agent = LlmAgent(
    name="FinalOutputAgent",
    model=MODEL,
    include_contents='none',
    instruction="""You are preparing the final version of a data story for delivery.

    **Final Story:**
    {{current_story}}

    Format the story with clear section headers and ensure it's ready for presentation.
    
    Output ONLY the formatted final story.
    """,
    description="Formats the final story for presentation",
    output_key=STATE_FINAL_STORY
)

# --- Overall Sequential Pipeline ---
root_agent = SequentialAgent(
    name="DataStorytellingPipeline",
    sub_agents=[
        story_generator_agent,  # Generate initial story
        refinement_loop,        # Run the critique/refine loop
        final_output_agent      # Format final output
    ],
    description="Generates a data story and iteratively refines it through self-critique until it meets quality standards"
) 