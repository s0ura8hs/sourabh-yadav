from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import json
import aiofiles
import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Portfolio API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Data directory for JSON storage
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Models
class ContactMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ContactMessageCreate(BaseModel):
    name: str
    email: str
    message: str

class ProjectData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    technologies: List[str]
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SkillData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    level: int
    category: str
    icon: Optional[str] = None

class WeatherData(BaseModel):
    location: str
    temperature: str
    description: str
    icon: str

# JSON file operations
async def read_json_file(filename: str) -> list:
    """Read data from JSON file"""
    file_path = DATA_DIR / f"{filename}.json"
    try:
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
            return json.loads(content) if content else []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

async def write_json_file(filename: str, data: list):
    """Write data to JSON file"""
    file_path = DATA_DIR / f"{filename}.json"
    async with aiofiles.open(file_path, 'w') as f:
        await f.write(json.dumps(data, indent=2, default=str))

# API Routes
@api_router.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Portfolio API is running", "status": "healthy"}

@api_router.post("/contact")
async def create_contact_message(contact_data: ContactMessageCreate):
    """Handle contact form submissions"""
    try:
        # Create contact message
        contact_message = ContactMessage(**contact_data.dict())
        
        # Read existing messages
        messages = await read_json_file("contact_messages")
        
        # Add new message
        messages.append(contact_message.dict())
        
        # Save to JSON file
        await write_json_file("contact_messages", messages)
        
        # Also save to MongoDB for backup
        await db.contact_messages.insert_one(contact_message.dict())
        
        return {"message": "Contact message sent successfully", "id": contact_message.id}
    
    except Exception as e:
        logging.error(f"Error creating contact message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send contact message")

@api_router.get("/contact", response_model=List[ContactMessage])
async def get_contact_messages():
    """Get all contact messages"""
    try:
        messages = await read_json_file("contact_messages")
        return [ContactMessage(**msg) for msg in messages]
    except Exception as e:
        logging.error(f"Error retrieving contact messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve contact messages")

@api_router.get("/weather")
async def get_weather():
    """Get weather data (mock implementation)"""
    try:
        # Mock weather data for now
        # In production, you would integrate with OpenWeatherMap API
        mock_weather = {
            "location": "New York, NY",
            "temperature": "22°C",
            "description": "Partly cloudy",
            "icon": "⛅"
        }
        return mock_weather
    except Exception as e:
        logging.error(f"Error fetching weather: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")

@api_router.post("/projects")
async def create_project(project_data: ProjectData):
    """Create a new project"""
    try:
        # Read existing projects
        projects = await read_json_file("projects")
        
        # Add new project
        projects.append(project_data.dict())
        
        # Save to JSON file
        await write_json_file("projects", projects)
        
        # Also save to MongoDB for backup
        await db.projects.insert_one(project_data.dict())
        
        return {"message": "Project created successfully", "id": project_data.id}
    
    except Exception as e:
        logging.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create project")

@api_router.get("/projects", response_model=List[ProjectData])
async def get_projects():
    """Get all projects"""
    try:
        projects = await read_json_file("projects")
        return [ProjectData(**project) for project in projects]
    except Exception as e:
        logging.error(f"Error retrieving projects: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve projects")

@api_router.post("/skills")
async def create_skill(skill_data: SkillData):
    """Create a new skill"""
    try:
        # Read existing skills
        skills = await read_json_file("skills")
        
        # Add new skill
        skills.append(skill_data.dict())
        
        # Save to JSON file
        await write_json_file("skills", skills)
        
        # Also save to MongoDB for backup
        await db.skills.insert_one(skill_data.dict())
        
        return {"message": "Skill created successfully", "id": skill_data.id}
    
    except Exception as e:
        logging.error(f"Error creating skill: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create skill")

@api_router.get("/skills", response_model=List[SkillData])
async def get_skills():
    """Get all skills"""
    try:
        skills = await read_json_file("skills")
        return [SkillData(**skill) for skill in skills]
    except Exception as e:
        logging.error(f"Error retrieving skills: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve skills")

@api_router.get("/github/{username}")
async def get_github_repos(username: str):
    """Get GitHub repositories for a user"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.github.com/users/{username}/repos")
            if response.status_code == 200:
                repos = response.json()
                # Return simplified repo data
                return [
                    {
                        "name": repo["name"],
                        "description": repo["description"],
                        "html_url": repo["html_url"],
                        "language": repo["language"],
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"]
                    }
                    for repo in repos[:10]  # Limit to 10 repos
                ]
            else:
                return []
    except Exception as e:
        logging.error(f"Error fetching GitHub repos: {str(e)}")
        return []

@api_router.get("/analytics")
async def get_analytics():
    """Get basic analytics data"""
    try:
        # Read data from JSON files
        contact_messages = await read_json_file("contact_messages")
        projects = await read_json_file("projects")
        
        analytics = {
            "total_contacts": len(contact_messages),
            "total_projects": len(projects),
            "last_contact": contact_messages[-1]["timestamp"] if contact_messages else None,
            "most_recent_project": projects[-1]["created_at"] if projects else None
        }
        
        return analytics
    except Exception as e:
        logging.error(f"Error retrieving analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")

# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("Portfolio API starting up...")
    
    # Create sample data if files don't exist
    try:
        # Sample skills data
        skills_data = [
            {"id": str(uuid.uuid4()), "name": "JavaScript", "level": 95, "category": "Frontend", "icon": "🟨"},
            {"id": str(uuid.uuid4()), "name": "Python", "level": 90, "category": "Backend", "icon": "🐍"},
            {"id": str(uuid.uuid4()), "name": "React", "level": 92, "category": "Frontend", "icon": "⚛️"},
            {"id": str(uuid.uuid4()), "name": "FastAPI", "level": 88, "category": "Backend", "icon": "🚀"},
            {"id": str(uuid.uuid4()), "name": "MongoDB", "level": 85, "category": "Database", "icon": "🍃"},
            {"id": str(uuid.uuid4()), "name": "Docker", "level": 82, "category": "DevOps", "icon": "🐋"}
        ]
        
        # Sample projects data
        projects_data = [
            {
                "id": str(uuid.uuid4()),
                "title": "Interactive Portfolio",
                "description": "A dynamic portfolio website with glittery particle effects",
                "technologies": ["React", "FastAPI", "MongoDB", "JavaScript"],
                "github_url": "https://github.com/johndoe/portfolio",
                "demo_url": "https://johndoe-portfolio.com",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Weather Dashboard",
                "description": "Real-time weather monitoring with beautiful visualizations",
                "technologies": ["Python", "Flask", "Weather API", "Chart.js"],
                "github_url": "https://github.com/johndoe/weather-dashboard",
                "demo_url": "https://weather-dashboard.com",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        # Initialize JSON files with sample data if they don't exist
        existing_skills = await read_json_file("skills")
        if not existing_skills:
            await write_json_file("skills", skills_data)
        
        existing_projects = await read_json_file("projects")
        if not existing_projects:
            await write_json_file("projects", projects_data)
        
        logger.info("Sample data initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing sample data: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Portfolio API shutting down...")
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)