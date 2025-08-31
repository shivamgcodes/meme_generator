# Meme Generator

## Overview

This is an AI-powered meme generation application that creates memes through a multi-step pipeline. The system uses Google Gemini for content planning and text generation, and Replicate for image generation. Users can specify themes, humor types, and content restrictions to generate customized memes via a command-line interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Pipeline Architecture
The application follows a sequential pipeline pattern with three main stages:
1. **Meme Planning**: Uses Gemini to conceptualize meme ideas based on user parameters
2. **Content Generation**: Generates appropriate text content for the planned meme
3. **Image Creation**: Uses Replicate's image generation models to create the final meme

### Component Structure
- **MemeGenerator**: Central orchestrator that manages the complete workflow from planning to file output
- **API Clients**: Separate client classes for Gemini and Replicate services with built-in error handling and retry logic
- **CLI Interface**: Command-line interface in main.py for user interaction with theme, humor type, and content restriction parameters
- **Utilities**: Helper functions for file operations and image downloading

### Error Handling Strategy
The system implements comprehensive error handling with:
- Graceful degradation when API calls fail
- Structured logging throughout the pipeline
- JSON parsing fallbacks for malformed API responses
- File system error handling for output operations

### Output Management
Generated memes are saved to a configurable output directory with sanitized filenames based on the content theme and generation timestamp.

## External Dependencies

### AI Services
- **Google Gemini API**: Primary service for content planning, text generation, and meme conceptualization
- **Replicate API**: Image generation service for creating visual meme content

### Python Libraries
- **google-genai**: Official Google Gemini client library
- **replicate**: Official Replicate API client
- **requests**: HTTP client for image downloading and web requests
- **pathlib**: Modern file path handling
- **json**: JSON parsing and manipulation
- **logging**: Comprehensive logging throughout the application

### Environment Configuration
- Requires GEMINI_API_KEY environment variable for Gemini authentication
- Requires REPLICATE_API_TOKEN environment variable for Replicate authentication
- Configurable output directory for generated meme files