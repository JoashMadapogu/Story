#!/usr/bin/env python3
# Data Storytelling Guide - Main Runner

from agent import (
    APP_NAME, USER_ID, SESSION_ID_BASE, 
    STATE_DATA_SOURCE, STATE_AUDIENCE, STATE_FINAL_STORY,
    STATE_USER_PREFERENCES, STATE_USER_FEEDBACK,
    root_agent
)
import google.generativeai as genai
from data_processor import processor
from preferences import preferences_manager
import uuid
import argparse
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY','AIzaSyBeCI4-rYSkFyfEPCKRw65d3WQP1eDBCGI'))

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

def collect_feedback():
    """Collect user feedback for story improvement and preference learning."""
    print("\nWould you like to provide feedback to improve future stories? (y/n)")
    response = input().lower()
    
    if response != 'y':
        return None
    
    feedback = {}
    
    # Collect tone preference
    print("\nPreferred tone for future stories? (formal/casual/technical/persuasive/balanced)")
    tone = input().lower()
    if tone in ['formal', 'casual', 'technical', 'persuasive', 'balanced']:
        feedback['tone_preference'] = tone
    
    # Collect format preference
    print("\nPreferred format for future stories? (standard/executive/detailed/bullet)")
    format_pref = input().lower()
    if format_pref in ['standard', 'executive', 'detailed', 'bullet']:
        feedback['format_preference'] = format_pref
    
    # Collect focus areas
    print("\nWhat areas should stories focus on? (comma-separated, e.g.: key_trends,outliers,recommendations)")
    focus = input()
    if focus:
        feedback['focus_areas'] = [area.strip() for area in focus.split(',')]
    
    # Collect general feedback
    print("\nAny other feedback or comments?")
    comments = input()
    if comments:
        feedback['general_comments'] = comments
    
    return feedback

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
            feedback = collect_feedback()
            if feedback:
                # Update user preferences with the feedback
                updated_prefs = preferences_manager.update_from_feedback(user_id, feedback)
                print(f"\nThank you for your feedback! Your preferences have been updated.")
                
                # Display the updated preferences
                print("\nUpdated preferences:")
                print(f"- Tone: {updated_prefs.get('tone', 'balanced')}")
                print(f"- Format: {updated_prefs.get('format', 'standard')}")
                print(f"- Focus areas: {', '.join(updated_prefs.get('focus_areas', []))}")
        
        return 0
    except Exception as e:
        print(f"Error executing agent: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 