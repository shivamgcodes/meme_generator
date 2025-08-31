"""
Main meme generation pipeline orchestrator.
Handles the complete workflow from planning to final meme creation.
"""

import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any

from api_clients import GeminiClient, ReplicateClient
from utils import save_image_from_url, sanitize_filename


class MemeGenerator:
    """Orchestrates the complete meme generation pipeline."""
    
    def __init__(self, output_dir: str = "output"):
        """Initialize the meme generator with API clients."""
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize API clients
        self.gemini_client = GeminiClient()
        self.replicate_client = ReplicateClient()
        
        self.logger.info("MemeGenerator initialized successfully")
    
    def generate_meme(self, theme: str, humor_type: str, restrictions: str, meme_index: int) -> Optional[str]:
        """
        Generate a single meme through the complete pipeline.
        
        Args:
            theme: Theme for the meme
            humor_type: Type of humor to use
            restrictions: Any content restrictions
            meme_index: Index of the current meme being generated
            
        Returns:
            Path to the generated meme file, or None if generation failed
        """
        try:
            # Step 1: Plan the meme
            self.logger.info("Step 1: Planning meme concept...")
            meme_plan = self._plan_meme(theme, humor_type, restrictions)
            if not meme_plan:
                self.logger.error("Failed to plan meme")
                return None
            
            # Step 2: Generate base image
            self.logger.info("Step 2: Generating base image...")
            image_url = self._generate_base_image(meme_plan)
            if not image_url:
                self.logger.error("Failed to generate base image")
                return None
            
            # Step 3: Download and save base image
            base_image_path = self.output_dir / f"base_image_{meme_index}_{int(time.time())}.jpg"
            if not save_image_from_url(image_url, str(base_image_path)):
                self.logger.error("Failed to download base image")
                return None
            
            # Step 4: Generate meme text
            self.logger.info("Step 3: Generating meme text...")
            meme_text = self._generate_meme_text(meme_plan, str(base_image_path))
            if not meme_text:
                self.logger.error("Failed to generate meme text")
                return None
            
            # Step 5: Apply text overlay using Gemini image generation
            self.logger.info("Step 4: Applying text overlay...")
            final_meme_path = self._apply_text_overlay_with_gemini(str(base_image_path), meme_text, meme_index)
            if not final_meme_path:
                self.logger.error("Failed to apply text overlay")
                return None
            
            self.logger.info(f"Meme generation completed successfully: {final_meme_path}")
            return final_meme_path
            
        except Exception as e:
            self.logger.error(f"Error in meme generation pipeline: {str(e)}")
            return None
    
    def _plan_meme(self, theme: str, humor_type: str, restrictions: str) -> Optional[Dict[str, Any]]:
        """Plan the meme concept using Gemini."""
        planning_prompt = f"""
        You are a creative meme strategist. Plan a meme with the following parameters:
        
        Theme: {theme}
        Humor Type: {humor_type}
        Restrictions: {restrictions if restrictions else "None"}
        
        Create a detailed meme plan that includes:
        1. Visual concept description for image generation
        2. Key visual elements that should be in the image
        3. Overall mood and style
        4. Text structure (how many text blocks will be needed)
        5. Brief description of the joke/humor concept
        
        Respond with a JSON object containing:
        {{
            "visual_concept": "detailed description for image generation",
            "visual_elements": ["element1", "element2", "element3"],
            "mood": "mood description",
            "style": "visual style",
            "text_blocks_needed": 2,
            "humor_concept": "brief description of the joke"
        }}
        """
        
        try:
            response = self.gemini_client.generate_json_response(planning_prompt)
            if response:
                self.logger.info(f"Meme plan: {response.get('humor_concept', 'N/A')}")
                return response
            return None
        except Exception as e:
            self.logger.error(f"Error planning meme: {str(e)}")
            return None
    
    def _generate_base_image(self, meme_plan: Dict[str, Any]) -> Optional[str]:
        """Generate base image using Replicate API."""
        visual_prompt = f"""
        {meme_plan.get('visual_concept', '')}
        
        Visual elements to include: {', '.join(meme_plan.get('visual_elements', []))}
        Mood: {meme_plan.get('mood', '')}
        Style: {meme_plan.get('style', '')}
        
        Create a clear, high-quality image suitable for meme text overlay.
        The image should have good contrast and space for text placement.
        Make it look like a typical meme template with clear areas for text.
        """
        
        try:
            image_url = self.replicate_client.generate_image(visual_prompt)
            if image_url:
                self.logger.info("Base image generated successfully")
                return image_url
            return None
        except Exception as e:
            self.logger.error(f"Error generating base image: {str(e)}")
            return None
    
    def _generate_meme_text(self, meme_plan: Dict[str, Any], image_path: str) -> Optional[Dict[str, Any]]:
        """Generate meme text using Gemini with image analysis."""
        text_prompt = f"""
        You are a meme text writer. Looking at this image, create funny meme text based on:
        
        Humor concept: {meme_plan.get('humor_concept', '')}
        Number of text blocks needed: {meme_plan.get('text_blocks_needed', 2)}
        
        Analyze the image and create appropriate meme text that:
        1. Fits the visual elements in the image
        2. Follows the humor concept
        3. Is properly structured for the number of text blocks needed
        4. Follows classic meme format (usually top text and bottom text)
        
        Respond with JSON:
        {{
            "text_blocks": [
                {{
                    "text": "TOP TEXT HERE",
                    "position": "top",
                    "style": "bold",
                    "color": "white"
                }},
                {{
                    "text": "BOTTOM TEXT HERE",
                    "position": "bottom", 
                    "style": "bold",
                    "color": "white"
                }}
            ]
        }}
        """
        
        try:
            response = self.gemini_client.analyze_image_and_generate_json(image_path, text_prompt)
            if response and 'text_blocks' in response:
                self.logger.info(f"Generated {len(response['text_blocks'])} text blocks")
                return response
            return None
        except Exception as e:
            self.logger.error(f"Error generating meme text: {str(e)}")
            return None
    
    def _apply_text_overlay_with_gemini(self, image_path: str, meme_text: Dict[str, Any], meme_index: int) -> Optional[str]:
        """Apply text overlay using Gemini image generation capabilities."""
        text_blocks = meme_text.get('text_blocks', [])
        
        # Create a comprehensive prompt for Gemini to generate the final meme
        text_descriptions = []
        for block in text_blocks:
            position = block.get('position', 'top')
            text = block.get('text', '')
            color = block.get('color', 'white')
            text_descriptions.append(f"{position.upper()} TEXT: '{text}' in {color} color with black outline")
        
        overlay_prompt = f"""
        Create a meme by adding text to this image. The text should be in classic meme font style (bold, impact-like font).
        
        Text to add:
        {' | '.join(text_descriptions)}
        
        Requirements:
        - Use bold, thick meme font (similar to Impact font)
        - Add black outline/stroke around all text for maximum readability
        - Make text large and clearly visible
        - Position top text near the top of the image
        - Position bottom text near the bottom of the image
        - Ensure text doesn't cover important visual elements
        - Use proper meme text formatting (ALL CAPS if appropriate)
        - Make sure the text is perfectly readable against the background
        
        Generate the final meme image with all text overlays applied.
        """
        
        try:
            # Use Gemini's image generation with the base image as context
            output_path = self.output_dir / f"final_meme_{meme_index}_{int(time.time())}.jpg"
            
            success = self.gemini_client.generate_meme_with_text_overlay(
                str(image_path), overlay_prompt, str(output_path)
            )
            
            if success:
                self.logger.info("Text overlay applied successfully using Gemini")
                return str(output_path)
            else:
                self.logger.error("Failed to apply text overlay with Gemini")
                return None
                
        except Exception as e:
            self.logger.error(f"Error applying text overlay: {str(e)}")
            return None
