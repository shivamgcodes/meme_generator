#!/usr/bin/env python3
"""
Command-line interface for the meme generator.
Usage: python main.py --theme "cats" --number 3 --humor-type "absurd" --restrictions "no profanity"
"""

import argparse
import logging
import sys
from pathlib import Path

from meme_generator import MemeGenerator
from utils import validate_environment


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('meme_generator.log')
        ]
    )


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate memes using AI pipeline with Gemini and Replicate APIs'
    )
    
    parser.add_argument(
        '--theme',
        type=str,
        required=True,
        help='Theme for the meme (e.g., "cats", "programming", "office humor")'
    )
    
    parser.add_argument(
        '--number',
        type=int,
        default=1,
        help='Number of memes to generate (default: 1)'
    )
    
    parser.add_argument(
        '--humor-type',
        type=str,
        default='general',
        help='Type of humor (e.g., "absurd", "witty", "dark", "wholesome", "general")'
    )
    
    parser.add_argument(
        '--restrictions',
        type=str,
        default='',
        help='Any restrictions or guidelines (e.g., "no profanity", "family-friendly")'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Directory to save generated memes (default: output)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the meme generator."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Validate environment variables first
        if not validate_environment():
            logger.error("Environment validation failed. Please set required API keys.")
            sys.exit(1)
        
        args = parse_arguments()
        
        logger.info("Starting meme generation pipeline...")
        logger.info(f"Theme: {args.theme}")
        logger.info(f"Number of memes: {args.number}")
        logger.info(f"Humor type: {args.humor_type}")
        logger.info(f"Restrictions: {args.restrictions}")
        
        # Create output directory if it doesn't exist
        output_path = Path(args.output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Initialize meme generator
        generator = MemeGenerator(output_dir=str(output_path))
        
        # Generate memes
        success_count = 0
        for i in range(args.number):
            logger.info(f"Generating meme {i+1}/{args.number}...")
            
            try:
                meme_path = generator.generate_meme(
                    theme=args.theme,
                    humor_type=args.humor_type,
                    restrictions=args.restrictions,
                    meme_index=i+1
                )
                
                if meme_path:
                    logger.info(f"Successfully generated meme: {meme_path}")
                    success_count += 1
                else:
                    logger.error(f"Failed to generate meme {i+1}")
                    
            except Exception as e:
                logger.error(f"Error generating meme {i+1}: {str(e)}")
                continue
        
        logger.info(f"Meme generation complete! Successfully generated {success_count}/{args.number} memes")
        
        if success_count == 0:
            logger.error("No memes were generated successfully")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Meme generation interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
