#!/usr/bin/env python3
# Data Storytelling Guide - Main Runner

from app.agent import (
    APP_NAME, USER_ID, SESSION_ID_BASE, 
    STATE_DATA_SOURCE, STATE_AUDIENCE, STATE_FINAL_STORY,
    STATE_USER_PREFERENCES, STATE_USER_FEEDBACK,
    root_agent
)
import google.generativeai as genai
from app.data_processor import processor
from app.preferences import preferences_manager
import uuid
import argparse
import json
import sys
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def parse_args():
    parser = argparse.ArgumentParser(description="Data Storytelling Guide")
    parser.add_argument("--data_source", required=True, help="Path to data file or description of data source")
    parser.add_argument("--audience", required=True, help="Target audience for the story (e.g., 'executives', 'technical team')")
    parser.add_argument("--output", help="Output file path (optional)")
    parser.add_argument("--user_id", default=USER_ID, help="User ID for preferences (optional)")
    parser.add_argument("--tone", help="Story tone (formal, casual, technical, persuasive, balanced)")
    parser.add_argument("--format", help="Story format (standard, executive, detailed, bullet)")
    parser.add_argument("--save_preferences", action="store_true", help="Save current preferences for future use")
    parser.add_argument("--focus", help="Comma-separated list of focus areas (e.g., 'key_trends,outliers,recommendations')")
    return parser.parse_args()

def refine_user_feedback(current_story: str, section_type: str, user_feedback: str) -> str:
    """
    Refine user feedback using LLM to ensure it's properly integrated into the story.
    
    Args:
        current_story (str): The current story text
        section_type (str): Type of section being updated
        user_feedback (str): Raw user feedback
        
    Returns:
        str: Refined feedback that maintains consistency with the story
    """
    model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
    
    refine_prompt = f"""Refine and integrate this user feedback for the {section_type} section of the story.

    Current Story:
    {current_story}

    User's Raw Feedback:
    {user_feedback}

    Task:
    1. Analyze the user's feedback and the current story
    2. Refine the feedback to maintain consistency with the story's tone and style
    3. Ensure the refined feedback aligns with the story's overall narrative
    4. Preserve the user's intent while making it fit naturally in the story
    5. Output the refined content for the {section_type} section

    Output only the refined content for the {section_type} section.
    """
    
    response = model.generate_content(refine_prompt)
    return response.text

def update_specific_section(current_story: str, section_type: str, new_content: str) -> str:
    """
    Update a specific section of the story with new content using LLM to maintain consistency.
    
    Args:
        current_story (str): The current story text
        section_type (str): Type of section to update ('title', 'introduction', 'insights', 'conclusion')
        new_content (str): New content or instructions for the section
        
    Returns:
        str: Updated story with LLM-refined section
    """
    # First, refine the user's feedback
    refined_content = refine_user_feedback(current_story, section_type, new_content)
    
    # Initialize the model
    model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
    
    # Create prompt for section update
    update_prompt = f"""Update the {section_type} section of this data story while maintaining consistency with the rest of the content.

    Current Story:
    {current_story}

    Refined Content for {section_type}:
    {refined_content}

    Task:
    1. Update the {section_type} section using the refined content
    2. Ensure the updated section maintains the same tone and style as the rest of the story
    3. Preserve the story's overall coherence and flow
    4. Keep all other sections unchanged
    5. Make sure the transition between sections is smooth

    Output the complete story with the updated section.
    """
    
    # Get LLM's response
    response = model.generate_content(update_prompt)
    return response.text

def get_user_input(prompt: str, default: str = None, valid_options: list = None) -> str:
    """
    Get user input with a default value and optional validation.
    
    Args:
        prompt (str): The prompt to show the user
        default (str): Default value if user just presses enter
        valid_options (list): List of valid options for validation
        
    Returns:
        str: User input or default value
    """
    if default:
        prompt = f"{prompt} (default: {default})"
    if valid_options:
        prompt = f"{prompt} [{'/'.join(valid_options)}]"
    prompt += ": "
    
    while True:
        user_input = input(prompt).strip()
        if not user_input and default:
            return default
        if not valid_options or user_input.lower() in [opt.lower() for opt in valid_options]:
            return user_input
        print(f"Please enter a valid option: {', '.join(valid_options)}")

def collect_story_feedback():
    """Collect user feedback for story improvement and preference learning."""
    feedback = {
        'timestamp': datetime.now().isoformat(),
        'preferences': {},
        'story_feedback': {}
    }
    
    # Collect tone preference
    tone = get_user_input(
        "\nPreferred tone for future stories",
        default="balanced",
        valid_options=['formal', 'casual', 'technical', 'persuasive', 'balanced']
    )
    feedback['preferences']['tone_preference'] = tone
    
    # Collect format preference
    format_pref = get_user_input(
        "\nPreferred format for future stories",
        default="standard",
        valid_options=['standard', 'executive', 'detailed', 'bullet']
    )
    feedback['preferences']['format_preference'] = format_pref
    
    # Collect focus areas
    focus = get_user_input(
        "\nWhat areas should stories focus on? (comma-separated)",
        default="key_trends,outliers,actionable_insights"
    )
    feedback['preferences']['focus_areas'] = [area.strip() for area in focus.split(',')]
    
    # Collect story-specific feedback
    update_section = get_user_input(
        "\nWould you like to update any section of the story?",
        default="n",
        valid_options=['y', 'n']
    )
    
    if update_section.lower() == 'y':
        section = get_user_input(
            "\nWhich section would you like to update?",
            valid_options=['title', 'introduction', 'insights', 'conclusion']
        )
        new_content = get_user_input(f"\nPlease provide your updated content for the {section}")
        feedback['story_feedback'][section] = new_content
    
    # Collect general feedback
    comments = get_user_input("\nAny other feedback or comments?", default="")
    if comments:
        feedback['general_comments'] = comments
    
    return feedback

def save_feedback(user_id: str, feedback: Dict[str, Any]):
    """Save user feedback to a feedback history file."""
    feedback_dir = "./user_feedback"
    if not os.path.exists(feedback_dir):
        os.makedirs(feedback_dir)
    
    feedback_file = os.path.join(feedback_dir, f"{user_id}_feedback.json")
    
    # Load existing feedback if any
    existing_feedback = []
    if os.path.exists(feedback_file):
        with open(feedback_file, 'r') as f:
            existing_feedback = json.load(f)
    
    # Append new feedback
    existing_feedback.append(feedback)
    
    # Save updated feedback
    with open(feedback_file, 'w') as f:
        json.dump(existing_feedback, f, indent=2)

def execute_agent_pipeline(initial_state):
    """Execute the agent pipeline using google.generativeai directly."""
    # Initialize the model
    model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
    
    # Generate initial story
    story_prompt = f"""Generate a data story based on:
    Data Source: {initial_state[STATE_DATA_SOURCE]}
    Target Audience: {initial_state[STATE_AUDIENCE]}
    User Preferences: {initial_state[STATE_USER_PREFERENCES]}
    
    Create a structured story with:
    1. A clear title
    2. Introduction explaining context
    3. 3-4 key insights with supporting narrative
    4. Conclusion or call-to-action
    """
    
    story_response = model.generate_content(story_prompt)
    current_story = story_response.text
    
    # Run critique loop
    max_iterations = 5
    for i in range(max_iterations):
        # Get critique
        critique_prompt = f"""Review this data story:
        {current_story}
        
        Data Source: {initial_state[STATE_DATA_SOURCE]}
        Target Audience: {initial_state[STATE_AUDIENCE]}
        User Preferences: {initial_state[STATE_USER_PREFERENCES]}
        
        Review for:
        1. Clarity
        2. Audience fit
        3. Insight value
        4. Coherence
        5. Completeness
        6. Preference alignment
        
        If improvements are needed, provide specific suggestions.
        If the story is satisfactory, respond with: "No significant improvements needed for this story."
        """
        
        critique_response = model.generate_content(critique_prompt)
        critique = critique_response.text
        
        # Check if story is satisfactory
        if "No significant improvements needed for this story" in critique:
            break
            
        # Refine story
        refine_prompt = f"""Refine this data story based on the following critique:
        Current Story:
        {current_story}
        
        Critique:
        {critique}
        
        Provide an improved version of the story that addresses all the feedback.
        """
        
        refine_response = model.generate_content(refine_prompt)
        current_story = refine_response.text
    
    # Format final output
    final_prompt = f"""Format this final data story for presentation:
    {current_story}
    
    Ensure clear section headers and professional formatting.
    """
    
    final_response = model.generate_content(final_prompt)
    return final_response.text

def main():
    args = parse_args()
    
    # Generate a unique session ID
    session_id = f"{SESSION_ID_BASE}_{uuid.uuid4().hex[:8]}"
    
    # Get the user ID (use provided or default)
    user_id = args.user_id
    
    # Process the data source
    processed_data = processor.process_data_source(args.data_source)
    
    # Get user preferences
    user_prefs = preferences_manager.get_user_preferences(user_id)
    
    # Override preferences with command line arguments if provided
    if args.tone:
        user_prefs['tone'] = args.tone
    if args.format:
        user_prefs['format'] = args.format
    if args.focus:
        user_prefs['focus_areas'] = args.focus.split(',')
        
    # Save preferences if requested
    if args.save_preferences:
        preferences_manager.save_user_preferences(user_id, user_prefs)
        print(f"Saved preferences for user {user_id}")
    
    # Initial state for the agent
    initial_state = {
        STATE_DATA_SOURCE: json.dumps(processed_data),
        STATE_AUDIENCE: args.audience,
        STATE_USER_PREFERENCES: json.dumps(user_prefs)
    }
    
    # Execute the agent pipeline
    print(f"Starting Data Storytelling Guide session {session_id}")
    print(f"Data source: {args.data_source}")
    print(f"Target audience: {args.audience}")
    print("Generating story with self-critique loop...\n")
    
    try:
        final_story = execute_agent_pipeline(initial_state)
        
        # Output the result
        if args.output:
            with open(args.output, 'w') as f:
                f.write(final_story)
            print(f"\nStory written to {args.output}")
        else:
            print("\n" + "="*50 + "\n")
            print("FINAL STORY:\n")
            print(final_story)
            print("\n" + "="*50)
        
        # Collect feedback if not in a file output mode
        if not args.output:
            print("\nWould you like to provide feedback? (y/n, default: n)")
            if get_user_input("", default="n", valid_options=['y', 'n']).lower() == 'y':
                feedback = collect_story_feedback()
                if feedback:
                    # Save feedback for future reference
                    save_feedback(user_id, feedback)
                    
                    # Update user preferences with the feedback
                    if 'preferences' in feedback:
                        updated_prefs = preferences_manager.update_from_feedback(user_id, feedback['preferences'])
                        print(f"\nThank you for your feedback! Your preferences have been updated.")
                        
                        # Display the updated preferences
                        print("\nUpdated preferences:")
                        print(f"- Tone: {updated_prefs.get('tone', 'balanced')}")
                        print(f"- Format: {updated_prefs.get('format', 'standard')}")
                        print(f"- Focus areas: {', '.join(updated_prefs.get('focus_areas', []))}")
                    
                    # Handle story-specific updates
                    if 'story_feedback' in feedback:
                        for section, new_content in feedback['story_feedback'].items():
                            final_story = update_specific_section(final_story, section, new_content)
                            print(f"\nUpdated {section} section of the story.")
                        
                        # Save the updated story
                        if args.output:
                            with open(args.output, 'w') as f:
                                f.write(final_story)
                        else:
                            print("\nUpdated Story:")
                            print(final_story)
        
        return 0
    except Exception as e:
        print(f"Error executing agent: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 