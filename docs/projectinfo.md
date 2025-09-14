# AI English-Chinese Dictionary Project

## Project Overview
An AI-powered bilingual dictionary web application that allows users to query English and Chinese word definitions using Google's Gemini API.

## Features
- **Bilingual Input Support**: Accept both English and Chinese text input
- **AI-Powered Definitions**: Utilize Gemini API for comprehensive word meanings
- **Web Interface**: Clean, responsive web UI with input field and results display
- **Real-time Translation**: Instant word lookup and definition retrieval

## Technical Stack
- **Backend**: Python (Flask/FastAPI)
- **Frontend**: HTML/CSS/JavaScript
- **AI Service**: Google Gemini API
- **Package Management**: UV
- **Testing**: Pytest
- **Code Quality**: Pre-commit hooks, Commitizen

## Project Structure
```
aiengdict/
├── main.py              # Main application entry point
├── src/                 # Source code directory
├── tests/               # Test files
├── static/              # Static files (CSS, JS, images)
├── templates/           # HTML templates
├── requirements.txt     # Dependencies
├── .env                 # Environment variables (API keys)
└── projectinfo.md       # This file
```

## Core Functionality
1. **Input Processing**:
   - Detect input language (Chinese/English)
   - Validate and sanitize user input

2. **API Integration**:
   - Connect to Gemini API
   - Send formatted queries for word definitions
   - Handle API responses and errors

3. **Response Formatting**:
   - Parse AI responses
   - Format definitions for web display
   - Handle multiple meanings and examples

## Development Phases

### Phase 1: Basic Setup
- [ ] Set up Flask/FastAPI web framework
- [ ] Create basic HTML template with input form
- [ ] Implement Gemini API integration
- [ ] Basic word lookup functionality

### Phase 2: Enhanced Features
- [ ] Language detection
- [ ] Improved UI/UX design
- [ ] Error handling and validation
- [ ] Response caching for performance

### Phase 3: Advanced Features
- [ ] Search history
- [ ] Pronunciation support
- [ ] Example sentences
- [ ] Word favorites/bookmarks

## Environment Setup
```bash
# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Add GEMINI_API_KEY to .env

# Run application
python main.py
```

## API Requirements
- **Gemini API Key**: Required for word definitions
- **Rate Limiting**: Consider API usage limits
- **Error Handling**: Graceful fallbacks for API failures

## Security Considerations
- Secure API key storage
- Input sanitization
- Rate limiting to prevent abuse
- HTTPS deployment

## Deployment
- **Development**: Local Flask server
- **Production**: Consider Gunicorn + Nginx
- **Cloud Options**: Google Cloud Run, Heroku, or similar

## Success Metrics
- Response time < 2 seconds
- Accurate translations for common words
- Clean, intuitive user interface
- Proper error handling for edge cases

## Future Enhancements
- Mobile-responsive design
- Offline word cache
- User accounts and preferences
- Advanced search filters
- Audio pronunciation
- Word of the day feature
