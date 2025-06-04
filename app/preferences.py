#!/usr/bin/env python3
# Data Storytelling Guide - User Preferences

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UserPreferences:
    """
    Module for managing user preferences in the Data Storytelling Guide.
    
    This module handles:
    1. Saving user preferences (tone, format, focus areas)
    2. Loading preferences for use in story generation
    3. Updating preferences based on feedback
    """
    
    VALID_TONES = ['formal', 'casual', 'technical', 'persuasive', 'balanced']
    VALID_FORMATS = ['standard', 'executive', 'detailed', 'bullet']
    DEFAULT_FOCUS_AREAS = ['key_trends', 'outliers', 'actionable_insights']
    
    def __init__(self, preferences_dir: str = "./user_preferences"):
        """
        Initialize the preferences manager.
        
        Args:
            preferences_dir (str): Directory to store preference files
        """
        self.preferences_dir = preferences_dir
        
        # Create preferences directory if it doesn't exist
        if not os.path.exists(preferences_dir):
            os.makedirs(preferences_dir)
            logger.info(f"Created preferences directory: {preferences_dir}")
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get preferences for a specific user.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            dict: User preferences or default preferences if none exist
        """
        pref_file = os.path.join(self.preferences_dir, f"{user_id}.json")
        
        if os.path.exists(pref_file):
            try:
                with open(pref_file, 'r') as f:
                    prefs = json.load(f)
                logger.info(f"Loaded preferences for user {user_id}")
                return self._validate_preferences(prefs)
            except Exception as e:
                logger.error(f"Error loading preferences for user {user_id}: {e}")
                return self._get_default_preferences()
        else:
            logger.info(f"No preferences found for user {user_id}, using defaults")
            return self._get_default_preferences()
    
    def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Save preferences for a specific user.
        
        Args:
            user_id (str): Unique identifier for the user
            preferences (dict): Preference data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        pref_file = os.path.join(self.preferences_dir, f"{user_id}.json")
        
        # Validate preferences before saving
        validated_prefs = self._validate_preferences(preferences)
        
        # Add timestamp for tracking
        validated_prefs['last_updated'] = datetime.now().isoformat()
        
        try:
            with open(pref_file, 'w') as f:
                json.dump(validated_prefs, f, indent=2)
            logger.info(f"Saved preferences for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving preferences for user {user_id}: {e}")
            return False
    
    def update_from_feedback(self, user_id: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update preferences based on user feedback.
        
        Args:
            user_id (str): Unique identifier for the user
            feedback (dict): Feedback data from the user
            
        Returns:
            dict: Updated preferences
        """
        current_prefs = self.get_user_preferences(user_id)
        
        # Extract preferences from feedback
        if 'tone_preference' in feedback:
            if feedback['tone_preference'] in self.VALID_TONES:
                current_prefs['tone'] = feedback['tone_preference']
            else:
                logger.warning(f"Invalid tone preference: {feedback['tone_preference']}")
        
        if 'format_preference' in feedback:
            if feedback['format_preference'] in self.VALID_FORMATS:
                current_prefs['format'] = feedback['format_preference']
            else:
                logger.warning(f"Invalid format preference: {feedback['format_preference']}")
        
        if 'focus_areas' in feedback:
            if isinstance(feedback['focus_areas'], list):
                current_prefs['focus_areas'] = feedback['focus_areas']
            else:
                logger.warning("Invalid focus areas format")
        
        # Save the updated preferences
        self.save_user_preferences(user_id, current_prefs)
        
        return current_prefs
    
    def _validate_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean user preferences.
        
        Args:
            preferences (dict): User preferences to validate
            
        Returns:
            dict: Validated preferences
        """
        validated = self._get_default_preferences()
        
        # Validate tone
        if 'tone' in preferences and preferences['tone'] in self.VALID_TONES:
            validated['tone'] = preferences['tone']
        
        # Validate format
        if 'format' in preferences and preferences['format'] in self.VALID_FORMATS:
            validated['format'] = preferences['format']
        
        # Validate focus areas
        if 'focus_areas' in preferences and isinstance(preferences['focus_areas'], list):
            validated['focus_areas'] = preferences['focus_areas']
        
        # Preserve timestamps if they exist
        if 'created_at' in preferences:
            validated['created_at'] = preferences['created_at']
        if 'last_updated' in preferences:
            validated['last_updated'] = preferences['last_updated']
        
        return validated
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default preferences for new users."""
        return {
            'tone': 'balanced',
            'format': 'standard',
            'focus_areas': self.DEFAULT_FOCUS_AREAS.copy(),
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }

# Singleton instance for use in other modules
preferences_manager = UserPreferences() 