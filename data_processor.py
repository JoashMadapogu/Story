#!/usr/bin/env python3
# Data Storytelling Guide - Data Processor

import os
import json
import pandas as pd
import numpy as np
from PIL import Image
import PyPDF2
from typing import Dict, List, Union, Optional

class DataProcessor:
    """
    Data processor for handling different data formats and extracting insights.
    
    This module is responsible for:
    1. Detecting file types (.png, .jpg, .pdf, .twb/.twbx, .pbix, .csv)
    2. Converting data to a format usable by the story generator
    3. Extracting basic insights when possible
    """
    
    def __init__(self):
        """Initialize the data processor with necessary components."""
        self.supported_image_formats = ['.png', '.jpg', '.jpeg']
        self.supported_document_formats = ['.pdf']
        self.supported_data_formats = ['.csv']
        self.supported_visualization_formats = ['.twb', '.twbx', '.pbix']
    
    def process_data_source(self, data_source: str) -> Dict:
        """
        Process a data source and extract relevant information for storytelling.
        
        Args:
            data_source (str): Path to file or description of data source
            
        Returns:
            dict: Structured data with insights for storytelling
        """
        # Check if data_source is a file path
        if os.path.isfile(data_source):
            return self._process_file(data_source)
        else:
            # Treat as a description of data
            return self._process_description(data_source)
    
    def _process_file(self, file_path: str) -> Dict:
        """Process different file types."""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Handle different file types
        if file_ext in self.supported_image_formats:
            return self._process_image(file_path)
        elif file_ext in self.supported_document_formats:
            return self._process_pdf(file_path)
        elif file_ext in self.supported_data_formats:
            return self._process_csv(file_path)
        elif file_ext in self.supported_visualization_formats:
            return self._process_visualization(file_path)
        else:
            return {
                "data_type": "unknown",
                "description": f"Unrecognized file format: {file_ext}",
                "insights": ["No automated insights available for this file type."]
            }
    
    def _process_description(self, description: str) -> Dict:
        """Process a text description of data."""
        return {
            "data_type": "description",
            "description": description,
            "insights": []  # No automated insights for descriptions
        }
    
    def _process_image(self, file_path: str) -> Dict:
        """Process an image file containing data visualization."""
        try:
            with Image.open(file_path) as img:
                # Basic image analysis
                width, height = img.size
                format = img.format
                
                return {
                    "data_type": "image",
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "description": f"Image file ({format}): {os.path.basename(file_path)}",
                    "metadata": {
                        "dimensions": f"{width}x{height}",
                        "format": format
                    },
                    "insights": ["Image data requires visual analysis."]
                }
        except Exception as e:
            return {
                "data_type": "image",
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "description": f"Image file: {os.path.basename(file_path)}",
                "error": str(e),
                "insights": ["Error processing image data."]
            }
    
    def _process_pdf(self, file_path: str) -> Dict:
        """Process a PDF file containing data."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                # Extract text from first page as sample
                first_page = pdf_reader.pages[0]
                sample_text = first_page.extract_text()[:500] + "..."
                
                return {
                    "data_type": "pdf",
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "description": f"PDF document: {os.path.basename(file_path)}",
                    "metadata": {
                        "pages": num_pages,
                        "sample_text": sample_text
                    },
                    "insights": ["PDF requires text extraction and analysis."]
                }
        except Exception as e:
            return {
                "data_type": "pdf",
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "description": f"PDF document: {os.path.basename(file_path)}",
                "error": str(e),
                "insights": ["Error processing PDF data."]
            }
    
    def _process_csv(self, file_path: str) -> Dict:
        """Process a CSV file."""
        try:
            df = pd.read_csv(file_path)
            
            # Basic statistical analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            stats = {}
            
            for col in numeric_cols:
                stats[col] = {
                    "mean": float(df[col].mean()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max())
                }
            
            return {
                "data_type": "csv",
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "description": f"CSV data file: {os.path.basename(file_path)}",
                "metadata": {
                    "rows": len(df),
                    "columns": list(df.columns),
                    "statistics": stats
                },
                "insights": [
                    f"Dataset contains {len(df)} rows and {len(df.columns)} columns.",
                    f"Numeric columns: {', '.join(numeric_cols)}"
                ]
            }
        except Exception as e:
            return {
                "data_type": "csv",
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "description": f"CSV data file: {os.path.basename(file_path)}",
                "error": str(e),
                "insights": ["Error processing CSV data."]
            }
    
    def _process_visualization(self, file_path: str) -> Dict:
        """Process visualization files (Tableau, Power BI)."""
        file_ext = os.path.splitext(file_path)[1].lower()
        tool = "Tableau" if file_ext in ['.twb', '.twbx'] else "Power BI"
        
        return {
            "data_type": "visualization",
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "description": f"{tool} file: {os.path.basename(file_path)}",
            "insights": [f"{tool} file requires specialized parsing."]
        }

# Singleton instance for use in other modules
processor = DataProcessor() 