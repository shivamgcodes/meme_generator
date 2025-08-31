# AI Meme Generator for Gravia Round 2

An intelligent meme generation pipeline that creates custom memes using AI. The system combines Google Gemini for content planning and text generation with Replicate for image generation, producing high-quality memes with perfect text overlays.

## Features

- **AI-Powered Pipeline**: Uses Gemini for planning and text generation, Replicate for image creation
- **Custom Themes**: Generate memes about any topic (cats, programming, coffee, office humor, etc.)
- **Multiple Humor Styles**: Support for different humor types (wholesome, witty, absurd, silly, etc.)
- **Perfect Text Overlay**: Gemini 2.5 Flash Image Generation ensures professional meme formatting
- **Content Restrictions**: Built-in support for family-friendly and custom content guidelines

## Quick Start

1. Set up your API keys (see Environment Variables section)
2. Run the generator:

```bash
python main.py --theme "cats" --number 1 --humor-type "wholesome"
```

3. Find your generated meme in the `output/` directory!

## Usage

### Basic Command

```bash
python main.py --theme "THEME" --number NUM --humor-type "TYPE"
```

### Command Line Arguments

| Parameter | Required | Default | Description | Examples |
|-----------|----------|---------|-------------|----------|
| `--theme` | ✅ Yes | - | Topic or theme for the meme | `"cats"`, `"programming"`, `"coffee"`, `"office humor"`, `"dogs"`, `"gaming"` |
| `--number` | No | `1` | Number of memes to generate | `1`, `3`, `5` |
| `--humor-type` | No | `general` | Style of humor to use | `"wholesome"`, `"witty"`, `"absurd"`, `"silly"`, `"relatable"`, `"dark"` |
| `--restrictions` | No | `""` | Content guidelines or restrictions | `"family-friendly"`, `"no profanity"`, `"workplace appropriate"` |
| `--output-dir` | No | `output` | Directory to save generated memes | `"my_memes"`, `"generated"` |

### Example Commands

```bash
# Generate a wholesome cat meme
python main.py --theme "cats" --number 1 --humor-type "wholesome"

# Generate 3 witty programming memes with family-friendly content
python main.py --theme "programming" --number 3 --humor-type "witty" --restrictions "family-friendly"

# Generate an absurd office humor meme
python main.py --theme "office humor" --number 1 --humor-type "absurd"

# Generate relatable coffee memes
python main.py --theme "coffee" --number 2 --humor-type "relatable"
```

## Environment Variables

You need to set up two API keys as environment variables:

### Required API Keys

| Variable | Service | Description | How to Get |
|----------|---------|-------------|------------|
| `GEMINI_API_KEY` | Google Gemini | Used for meme planning, text generation, and text overlay | Visit [Google AI Studio](https://aistudio.google.com), sign in, and create an API key |
| `REPLICATE_API_TOKEN` | Replicate | Used for base image generation | Visit [Replicate](https://replicate.com), create an account, and get your API token from account settings |

### Setting Up API Keys

1. **Get Gemini API Key:**
   - Go to [Google AI Studio](https://aistudio.google.com)
   - Sign in with your Google account
   - Create a new API key
   - Copy the key

2. **Get Replicate API Token:**
   - Go to [Replicate](https://replicate.com)
   - Create a free account
   - Go to your account settings
   - Copy your API token

3. **Set Environment Variables:**
   - In Replit: Add them to your Secrets tab
   - Locally: Add to your `.env` file or export them:
   ```bash
   export GEMINI_API_KEY="your_gemini_key_here"
   export REPLICATE_API_TOKEN="your_replicate_token_here"
   ```

## How It Works

The meme generation follows a 4-step AI pipeline:

1. **🎯 Meme Planning**: Gemini analyzes your theme and humor type to create a detailed meme concept
2. **🖼️ Image Generation**: Replicate generates a custom base image based on the planned concept
3. **📝 Text Creation**: Gemini analyzes the generated image and creates appropriate meme text
4. **🎨 Text Overlay**: Gemini 2.5 Flash Image Generation applies the text with perfect meme formatting

## Output

Generated memes are saved to the specified output directory with descriptive filenames:
- `final_meme_1_[timestamp].jpg` - Your finished meme with text overlay
- `base_image_1_[timestamp].jpg` - The original generated image (before text)

## Requirements

- Python 3.11+
- Internet connection for API calls
- Valid API keys for Gemini and Replicate

## Dependencies

The following packages are automatically installed:
- `google-genai` - Google Gemini API client
- `replicate` - Replicate API client  
- `requests` - For downloading generated images

## Examples of Generated Memes

- **Cats + Wholesome**: Peaceful sleeping kitten with text about wanting simple comfort
- **Programming + Witty**: Tangled lights representing debugging complex code
- **Coffee + Relatable**: Before/after coffee transformation split image
- **Dogs + Silly**: Golden Retriever "learning to code" with paw problems

## Troubleshooting

**Common Issues:**

- **Missing API Keys**: Make sure both `GEMINI_API_KEY` and `REPLICATE_API_TOKEN` are set
- **Generation Failures**: Check your internet connection and API key validity
- **No Output**: Verify the output directory exists and is writable

**Check Logs:**
The system creates detailed logs in `meme_generator.log` for debugging any issues.

---

Ready to create some amazing memes? Just run the command with your favorite theme and watch the AI magic happen! 🎭
