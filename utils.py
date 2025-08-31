"""
Utility functions for the meme generator.
"""

import logging
import re
import requests
from pathlib import Path
from typing import Optional


def save_image_from_url(url: str, output_path: str) -> bool:
    """
    Download and save an image from a URL.
    
    Args:
        url: URL of the image to download
        output_path: Local path where the image should be saved
        
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Downloading image from: {url}")
        
        # Make request with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save the image
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Image saved successfully to: {output_path}")
        return True
        
    except requests.RequestException as e:
        logger.error(f"Error downloading image: {e}")
        return False
    except Exception as e:
        logger.error(f"Error saving image: {e}")
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing or replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem use
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "untitled"
    
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    return sanitized


def validate_environment() -> bool:
    """
    Validate that all required environment variables are set.
    
    Returns:
        True if all required variables are present, False otherwise
    """
    import os
    
    logger = logging.getLogger(__name__)
    required_vars = ['GEMINI_API_KEY', 'REPLICATE_API_TOKEN']
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("All required environment variables are present")
    return True


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes = size_bytes / 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def get_image_info(image_path: str) -> Optional[dict]:
    """
    Get basic information about an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with image info or None if error
    """
    try:
        from PIL import Image
        
        with Image.open(image_path) as img:
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size_bytes': Path(image_path).stat().st_size,
                'size_formatted': format_file_size(Path(image_path).stat().st_size)
            }
    except Exception:
        return None


def create_output_directory(base_dir: str = "output") -> Path:
    """
    Create output directory with timestamp subdirectory.
    
    Args:
        base_dir: Base directory name
        
    Returns:
        Path object for the created directory
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(base_dir) / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir


def log_generation_stats(stats: dict):
    """
    Log generation statistics in a formatted way.
    
    Args:
        stats: Dictionary containing generation statistics
    """
    logger = logging.getLogger(__name__)
    
    logger.info("=== MEME GENERATION STATISTICS ===")
    for key, value in stats.items():
        logger.info(f"{key}: {value}")
    logger.info("=" * 35)
