"""
API client implementations for Gemini and Replicate services.
"""

import json
import logging
import os
import time
from typing import Optional, Dict, Any

import replicate
from google import genai
from google.genai import types


class GeminiClient:
    """Client for interacting with Google Gemini API."""
    
    def __init__(self):
        """Initialize Gemini client with API key from environment."""
        self.logger = logging.getLogger(__name__)
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        self.client = genai.Client(api_key=api_key)
        self.logger.info("Gemini client initialized successfully")
    
    def generate_json_response(self, prompt: str, model: str = "gemini-2.5-flash") -> Optional[Dict[str, Any]]:
        """Generate a JSON response from Gemini."""
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            if response.text:
                return json.loads(response.text)
            return None
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            # Try to extract JSON from response text
            try:
                text = response.text if response.text else ""
                # Look for JSON-like content
                start = text.find('{')
                end = text.rfind('}') + 1
                if start != -1 and end > start:
                    json_text = text[start:end]
                    return json.loads(json_text)
            except:
                pass
            return None
        except Exception as e:
            self.logger.error(f"Error generating JSON response: {e}")
            return None
    
    def analyze_image_and_generate_json(self, image_path: str, prompt: str, model: str = "gemini-2.5-flash") -> Optional[Dict[str, Any]]:
        """Analyze an image and generate a JSON response."""
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            
            response = self.client.models.generate_content(
                model=model,
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg"
                    ),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            if response.text:
                return json.loads(response.text)
            return None
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            # Try to extract JSON from response text
            try:
                text = response.text if response.text else ""
                start = text.find('{')
                end = text.rfind('}') + 1
                if start != -1 and end > start:
                    json_text = text[start:end]
                    return json.loads(json_text)
            except:
                pass
            return None
        except Exception as e:
            self.logger.error(f"Error analyzing image: {e}")
            return None
    
    def generate_meme_with_text_overlay(self, image_path: str, prompt: str, output_path: str) -> bool:
        """Generate a meme with text overlay using Gemini's image generation capabilities."""
        try:
            # First analyze the image and create a comprehensive prompt
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            
            # Create a detailed prompt for recreating the image with text
            analysis_prompt = f"""
            Analyze this image and describe it in detail for recreation purposes.
            Then create a new version of this exact same image but with meme text added as specified:
            
            {prompt}
            
            Recreate the image maintaining all visual elements, colors, composition, and style,
            but add the specified meme text with proper formatting.
            """
            
            # Try using the image generation model
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash-preview-image-generation",
                    contents=[
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type="image/jpeg"
                        ),
                        analysis_prompt
                    ],
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT', 'IMAGE']
                    )
                )
                
                if response.candidates:
                    content = response.candidates[0].content
                    if content and content.parts:
                        # Look for image data in response
                        for part in content.parts:
                            if part.inline_data and part.inline_data.data:
                                with open(output_path, 'wb') as f:
                                    f.write(part.inline_data.data)
                                self.logger.info(f"Meme with text overlay saved to {output_path}")
                                return True
                            elif part.text:
                                self.logger.info(f"Gemini response: {part.text}")
                
            except Exception as gen_error:
                self.logger.warning(f"Image generation model failed: {gen_error}")
                
                # Fallback: Use Gemini to analyze and provide detailed instructions for Replicate
                analysis_response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type="image/jpeg"
                        ),
                        f"""
                        Analyze this image and create a detailed prompt for regenerating it with meme text.
                        
                        {prompt}
                        
                        Create a comprehensive image generation prompt that:
                        1. Describes the current image in detail
                        2. Specifies where and how to add the meme text
                        3. Ensures the text is readable and properly formatted
                        
                        Format your response as a single detailed prompt for image generation.
                        """
                    ]
                )
                
                if analysis_response.text:
                    # Use this enhanced prompt with Replicate to generate the final meme
                    enhanced_prompt = analysis_response.text
                    return self._generate_final_meme_with_replicate(enhanced_prompt, output_path)
            
            self.logger.error("No image data found in Gemini response")
            return False
            
        except Exception as e:
            self.logger.error(f"Error generating meme with text overlay: {e}")
            return False
    
    def _generate_final_meme_with_replicate(self, prompt: str, output_path: str) -> bool:
        """Fallback method to generate final meme using Replicate."""
        try:
            from utils import save_image_from_url
            
            # Use Replicate to generate the final meme
            output = replicate.run(
                "black-forest-labs/flux-1.1-pro",
                input={
                    "prompt": prompt,
                    "aspect_ratio": "16:9",
                    "output_format": "jpg",
                    "safety_tolerance": 2,
                    "prompt_upsampling": True
                }
            )
            
            # Handle output
            image_url = None
            if isinstance(output, list) and len(output) > 0:
                # Handle FileOutput objects
                first_item = output[0]
                if hasattr(first_item, 'url'):
                    image_url = first_item.url
                else:
                    image_url = str(first_item)
            elif isinstance(output, str):
                image_url = output
            elif hasattr(output, 'url'):
                # Handle single FileOutput object
                image_url = output.url
            else:
                # Try to convert to string as fallback
                image_url = str(output)
            
            if image_url:
                if save_image_from_url(image_url, output_path):
                    self.logger.info(f"Fallback meme generation successful: {output_path}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Fallback meme generation failed: {e}")
            return False


class ReplicateClient:
    """Client for interacting with Replicate API."""
    
    def __init__(self):
        """Initialize Replicate client with API key from environment."""
        self.logger = logging.getLogger(__name__)
        api_token = os.getenv("REPLICATE_API_TOKEN")
        
        if not api_token:
            raise ValueError("REPLICATE_API_TOKEN environment variable is required")
        
        # Set the API token for replicate
        os.environ["REPLICATE_API_TOKEN"] = api_token
        self.logger.info("Replicate client initialized successfully")
    
    def generate_image(self, prompt: str, model: str = "black-forest-labs/flux-1.1-pro") -> Optional[str]:
        """Generate an image using Replicate API."""
        try:
            self.logger.info(f"Generating image with prompt: {prompt[:100]}...")
            
            # Use Flux model for high-quality image generation
            output = replicate.run(
                model,
                input={
                    "prompt": prompt,
                    "aspect_ratio": "16:9",
                    "output_format": "jpg",
                    "safety_tolerance": 2,
                    "prompt_upsampling": True
                }
            )
            
            # Handle different output formats
            if isinstance(output, list) and len(output) > 0:
                # Handle FileOutput objects
                first_item = output[0]
                if hasattr(first_item, 'url'):
                    image_url = first_item.url
                else:
                    image_url = str(first_item)
            elif isinstance(output, str):
                image_url = output
            elif hasattr(output, 'url'):
                # Handle single FileOutput object
                image_url = output.url
            else:
                # Try to convert to string as fallback
                image_url = str(output)
                self.logger.warning(f"Converting unexpected output format {type(output)} to string: {image_url}")
            
            self.logger.info(f"Image generated successfully: {image_url}")
            return image_url
            
        except Exception as e:
            self.logger.error(f"Error generating image with {model}: {e}")
            # Fallback to different model if primary fails
            try:
                self.logger.info("Trying fallback model...")
                output = replicate.run(
                    "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
                    input={
                        "prompt": prompt,
                        "width": 1024,
                        "height": 576,
                        "num_outputs": 1,
                        "scheduler": "K_EULER",
                        "num_inference_steps": 20,
                        "guidance_scale": 7.5
                    }
                )
                
                if isinstance(output, list) and len(output) > 0:
                    self.logger.info("Fallback model succeeded")
                    return output[0]
                elif isinstance(output, str):
                    return output
                    
            except Exception as fallback_error:
                self.logger.error(f"Fallback model also failed: {fallback_error}")
            
            return None
    
    def wait_for_completion(self, prediction_id: str, max_wait_time: int = 300) -> Optional[str]:
        """Wait for a prediction to complete and return the result."""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                prediction = replicate.predictions.get(prediction_id)
                
                if prediction.status == "succeeded":
                    if prediction.output:
                        return prediction.output[0] if isinstance(prediction.output, list) else prediction.output
                elif prediction.status == "failed":
                    self.logger.error(f"Prediction failed: {prediction.error}")
                    return None
                elif prediction.status in ["starting", "processing"]:
                    self.logger.info(f"Prediction status: {prediction.status}")
                    time.sleep(5)
                else:
                    self.logger.warning(f"Unknown prediction status: {prediction.status}")
                    time.sleep(5)
                    
            except Exception as e:
                self.logger.error(f"Error checking prediction status: {e}")
                time.sleep(5)
        
        self.logger.error("Prediction timed out")
        return None
