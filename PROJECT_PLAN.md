# Person Research Agent - Development Plan

## Project Overview
A Python-based research agent that collects publicly available information about individuals from various online sources.

## Tech Stack
- **Backend**: Python + FastAPI
- **Database**: SQLite (starting simple, can upgrade later)
- **Interface**: CLI (Phase 1) → Web Interface (Phase 5)
- **Key Libraries**: requests, beautifulsoup4, python-dotenv, sqlite3

## Development Phases

### Phase 1: Foundation ✅ (Current)
**Goal**: Basic CLI interface with simple web search

**Features**:
- CLI interface to accept person's name and optional info
- Basic Google search functionality
- Simple result parsing and display
- Project structure setup
- Virtual environment and dependencies

**Deliverables**:
- `main.py` - CLI entry point
- `research_agent.py` - Core research logic
- `requirements.txt` - Dependencies
- Basic search and display functionality

### Phase 2: Enhanced Web Search
**Goal**: Improve search capabilities and data handling

**Features**:
- Enhanced Google search with better parsing
- Basic web scraping for public information
- JSON file storage for results
- Error handling and logging
- Search result filtering and ranking

**Deliverables**:
- Improved search algorithms
- Data persistence layer
- Better result formatting
- Error handling system

### Phase 3: Social Media Integration
**Goal**: Add LinkedIn and X (Twitter) search capabilities

**Features**:
- LinkedIn public profile search
- Twitter/X profile and post search
- Platform-specific data extraction
- Data correlation between platforms

**Deliverables**:
- LinkedIn integration module
- Twitter/X integration module
- Cross-platform data matching
- Enhanced data models

### Phase 4: Data Management
**Goal**: Implement proper database and data management

**Features**:
- SQLite database implementation
- Person data models and relationships
- Search history and caching
- Data deduplication
- Query optimization

**Deliverables**:
- Database schema and models
- Data access layer
- Caching system
- Search history functionality

### Phase 5: Web Interface
**Goal**: Create web-based interface using FastAPI

**Features**:
- FastAPI web server
- HTML templates for search interface
- Real-time search progress
- View past searches
- Export functionality (JSON/CSV)

**Deliverables**:
- FastAPI web application
- Frontend templates
- API endpoints
- Export functionality

### Phase 6: Advanced Features
**Goal**: Add sophisticated research capabilities

**Features**:
- Additional platforms (Instagram, Facebook public pages)
- Image recognition for profile matching
- Advanced data correlation algorithms
- Automated report generation
- Search scheduling and monitoring

**Deliverables**:
- Multi-platform integration
- AI-powered data correlation
- Report generation system
- Advanced search features

## Platform Research Capabilities

### Google Web Search
- General web presence
- News articles and mentions
- Professional websites
- Public records

### LinkedIn
- Professional background
- Current employment
- Professional connections
- Skills and endorsements

### X (Twitter)
- Public tweets and engagement
- Follower/following analysis
- Tweet sentiment and topics
- Public interaction patterns

### Future Platforms
- Instagram (public profiles)
- Facebook (public pages/posts)
- GitHub (for developers)
- Professional directories
- News and media mentions

## Data Output Format
**Paragraph Format**: All collected information will be formatted into readable paragraphs organized by source platform and information type.

## Technical Considerations

### Legal and Ethical
- Only public information
- Respect robots.txt and terms of service
- Rate limiting to avoid overloading servers
- No storage of sensitive personal information

### Performance
- Asynchronous processing for multiple sources
- Caching to avoid duplicate requests
- Progress indicators for long-running searches
- Configurable timeout settings

### Security
- Secure API key management
- Input validation and sanitization
- No storage of authentication credentials
- Local data storage only

## File Structure
```
Research Agent/
├── main.py                 # CLI entry point
├── research_agent.py       # Core research logic
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── database/
│   └── models.py          # Database models (Phase 4)
├── platforms/
│   ├── google_search.py   # Google search module
│   ├── linkedin.py        # LinkedIn integration
│   └── twitter.py         # Twitter/X integration
├── utils/
│   ├── data_formatter.py  # Output formatting
│   ├── storage.py         # Data storage utilities
│   └── validators.py      # Input validation
└── web/                   # FastAPI web interface (Phase 5)
    ├── app.py
    ├── templates/
    └── static/
```

## Getting Started
1. Set up Python virtual environment
2. Install dependencies from requirements.txt
3. Configure environment variables
4. Run CLI interface: `python main.py`

## Next Steps
- Complete Phase 1 implementation
- Test basic search functionality
- Plan Phase 2 enhancements
- Gather feedback and iterate 