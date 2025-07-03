from fastapi import FastAPI, APIRouter, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime
import json
import aiofiles
import httpx
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
import base64

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

# Email Configuration
try:
    conf = ConnectionConfig(
        MAIL_USERNAME=os.getenv("GMAIL_USER", "sourabhkhairwal@gmail.com"),
        MAIL_PASSWORD=os.getenv("GMAIL_PASSWORD", ""),  # Will be set via environment
        MAIL_FROM=os.getenv("GMAIL_USER", "sourabhkhairwal@gmail.com"),
        MAIL_PORT=587,
        MAIL_SERVER="smtp.gmail.com",
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )
    email_enabled = bool(os.getenv("GMAIL_PASSWORD"))
except Exception as e:
    logging.warning(f"Email configuration failed: {e}")
    email_enabled = False

# Models
class ContactMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ContactMessageCreate(BaseModel):
    name: str
    email: EmailStr
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

class EducationData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    degree: str
    school: str
    year: str
    description: str
    type: str  # "education" or "certification"
    icon: Optional[str] = None
    certificate_url: Optional[str] = None  # New field for certificate links

class PhotographyData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    camera: str
    settings: str
    location: str
    image_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WeatherData(BaseModel):
    location: str
    temperature: str
    description: str
    icon: str

class ResumeData(BaseModel):
    personal_info: dict
    experience: List[dict]
    education: List[dict]
    skills: List[dict]
    projects: List[dict]

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

# Email sending function
async def send_email(subject: str, recipient: str, html_content: str) -> bool:
    """Send email using Gmail SMTP"""
    if not email_enabled:
        logging.warning("Email not configured. Message would be: " + html_content)
        return False
    
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[recipient],
            body=html_content,
            subtype=MessageType.html
        )
        
        fm = FastMail(conf)
        await fm.send_message(message)
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return False

# PDF Resume Generator
def generate_resume_pdf(resume_data: dict) -> bytes:
    """Generate ATS-friendly PDF resume"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30, alignment=TA_CENTER, textColor=colors.black)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, spaceAfter=12, textColor=colors.black, fontName='Helvetica-Bold')
    subheading_style = ParagraphStyle('CustomSubheading', parent=styles['Heading3'], fontSize=12, spaceBefore=6, spaceAfter=6, textColor=colors.black, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, spaceAfter=6, textColor=colors.black)
    
    # Build content
    story = []
    
    # Header
    personal = resume_data.get('personal_info', {})
    story.append(Paragraph(personal.get('name', 'Sourabh Khairwal'), title_style))
    
    contact_info = f"""
    {personal.get('email', 'sourabhkhairwal@gmail.com')} | {personal.get('phone', '+91 XXXXX XXXXX')} | 
    {personal.get('location', 'India')} | {personal.get('linkedin', 'linkedin.com/in/sourabhkhairwal')}
    """
    story.append(Paragraph(contact_info, normal_style))
    story.append(Spacer(1, 12))
    
    # Professional Summary
    if personal.get('summary'):
        story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
        story.append(Paragraph(personal.get('summary'), normal_style))
        story.append(Spacer(1, 12))
    
    # Experience
    experience = resume_data.get('experience', [])
    if experience:
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", heading_style))
        for exp in experience:
            story.append(Paragraph(f"<b>{exp.get('title', '')}</b> | {exp.get('company', '')}", subheading_style))
            story.append(Paragraph(f"{exp.get('duration', '')} | {exp.get('location', '')}", normal_style))
            
            if exp.get('responsibilities'):
                for resp in exp.get('responsibilities', []):
                    story.append(Paragraph(f"• {resp}", normal_style))
            story.append(Spacer(1, 8))
    
    # Education
    education = resume_data.get('education', [])
    if education:
        story.append(Paragraph("EDUCATION", heading_style))
        for edu in education:
            story.append(Paragraph(f"<b>{edu.get('degree', '')}</b>", subheading_style))
            story.append(Paragraph(f"{edu.get('school', '')} | {edu.get('year', '')}", normal_style))
            if edu.get('description'):
                story.append(Paragraph(edu.get('description'), normal_style))
            story.append(Spacer(1, 8))
    
    # Skills
    skills = resume_data.get('skills', [])
    if skills:
        story.append(Paragraph("TECHNICAL SKILLS", heading_style))
        
        # Group skills by category
        skill_categories = {}
        for skill in skills:
            category = skill.get('category', 'General')
            if category not in skill_categories:
                skill_categories[category] = []
            skill_categories[category].append(skill.get('name'))
        
        for category, skill_list in skill_categories.items():
            skills_text = f"<b>{category}:</b> " + ", ".join(skill_list)
            story.append(Paragraph(skills_text, normal_style))
        story.append(Spacer(1, 12))
    
    # Projects
    projects = resume_data.get('projects', [])
    if projects:
        story.append(Paragraph("KEY PROJECTS", heading_style))
        for proj in projects:
            story.append(Paragraph(f"<b>{proj.get('title', '')}</b>", subheading_style))
            story.append(Paragraph(proj.get('description', ''), normal_style))
            if proj.get('technologies'):
                tech_text = f"<b>Technologies:</b> {', '.join(proj.get('technologies', []))}"
                story.append(Paragraph(tech_text, normal_style))
            story.append(Spacer(1, 8))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# API Routes
@api_router.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Portfolio API is running", "status": "healthy"}

@api_router.post("/contact")
async def create_contact_message(contact_data: ContactMessageCreate):
    """Handle contact form submissions with email notification"""
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
        
        # Send email notification
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5aa0; border-bottom: 2px solid #2c5aa0; padding-bottom: 10px;">
                    New Contact Form Submission - Sourabh Portfolio
                </h2>
                <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Name:</strong> {contact_data.name}</p>
                    <p><strong>Email:</strong> {contact_data.email}</p>
                    <p><strong>Message:</strong></p>
                    <div style="background-color: white; padding: 15px; border-left: 4px solid #2c5aa0; margin-top: 10px;">
                        {contact_data.message}
                    </div>
                </div>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="color: #666; font-size: 12px;">
                    Submitted at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC<br>
                    Message ID: {contact_message.id}
                </p>
            </div>
        </body>
        </html>
        """
        
        email_sent = await send_email(
            subject=f"New Contact Form Submission from {contact_data.name}",
            recipient="sourabhkhairwal@gmail.com",
            html_content=html_content
        )
        
        return {
            "message": "Contact message sent successfully", 
            "id": contact_message.id,
            "email_sent": email_sent
        }
    
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
        projects = await read_json_file("projects")
        projects.append(project_data.dict())
        await write_json_file("projects", projects)
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
        skills = await read_json_file("skills")
        skills.append(skill_data.dict())
        await write_json_file("skills", skills)
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

@api_router.post("/education")
async def create_education(education_data: EducationData):
    """Create a new education or certification entry"""
    try:
        education = await read_json_file("education")
        education.append(education_data.dict())
        await write_json_file("education", education)
        await db.education.insert_one(education_data.dict())
        return {"message": "Education entry created successfully", "id": education_data.id}
    except Exception as e:
        logging.error(f"Error creating education entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create education entry")

@api_router.get("/education", response_model=List[EducationData])
async def get_education():
    """Get all education and certification entries"""
    try:
        education = await read_json_file("education")
        return [EducationData(**edu) for edu in education]
    except Exception as e:
        logging.error(f"Error retrieving education data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve education data")

@api_router.post("/photography")
async def create_photography(photography_data: PhotographyData):
    """Create a new photography entry"""
    try:
        photography = await read_json_file("photography")
        photography.append(photography_data.dict())
        await write_json_file("photography", photography)
        await db.photography.insert_one(photography_data.dict())
        return {"message": "Photography entry created successfully", "id": photography_data.id}
    except Exception as e:
        logging.error(f"Error creating photography entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create photography entry")

@api_router.get("/photography", response_model=List[PhotographyData])
async def get_photography():
    """Get all photography entries"""
    try:
        photography = await read_json_file("photography")
        return [PhotographyData(**photo) for photo in photography]
    except Exception as e:
        logging.error(f"Error retrieving photography data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve photography data")

@api_router.get("/resume/generate")
async def generate_resume():
    """Generate and download PDF resume"""
    try:
        # Gather all data for resume
        skills = await read_json_file("skills")
        projects = await read_json_file("projects")
        education = await read_json_file("education")
        
        # Sample personal info (you can make this configurable)
        personal_info = {
            "name": "Sourabh Khairwal",
            "email": "sourabhkhairwal@gmail.com",
            "phone": "+91 XXXXX XXXXX",
            "location": "India",
            "linkedin": "linkedin.com/in/sourabhkhairwal",
            "summary": "Full-Stack Developer & Creative Technologist with expertise in React, Python, and interactive web applications. Passionate about creating digital experiences that combine cutting-edge technology with creative design. Experienced in neural network visualizations, particle systems, and photography portfolio development."
        }
        
        # Sample experience (you can make this configurable)
        experience = [
            {
                "title": "Senior Full-Stack Developer",
                "company": "Tech Solutions Inc.",
                "duration": "2022 - Present",
                "location": "Remote",
                "responsibilities": [
                    "Developed interactive portfolio websites with neural network animations and particle systems",
                    "Built responsive web applications using React, FastAPI, and MongoDB",
                    "Implemented real-time data visualization and photography gallery systems",
                    "Integrated email services and PDF generation for client communications"
                ]
            },
            {
                "title": "Frontend Developer",
                "company": "Creative Digital Agency",
                "duration": "2020 - 2022",
                "location": "India",
                "responsibilities": [
                    "Created dynamic user interfaces with advanced CSS animations and JavaScript",
                    "Developed photography portfolio websites with interactive slideshows",
                    "Collaborated with design teams to implement pixel-perfect layouts"
                ]
            }
        ]
        
        resume_data = {
            "personal_info": personal_info,
            "experience": experience,
            "education": [edu for edu in education if edu.get('type') == 'education'],
            "skills": skills,
            "projects": projects[:3]  # Top 3 projects
        }
        
        # Generate PDF
        pdf_bytes = generate_resume_pdf(resume_data)
        
        # Return PDF as response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=Sourabh_Khairwal_Resume.pdf"
            }
        )
    
    except Exception as e:
        logging.error(f"Error generating resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate resume")

@api_router.get("/github/{username}")
async def get_github_repos(username: str):
    """Get GitHub repositories for a user"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.github.com/users/{username}/repos")
            if response.status_code == 200:
                repos = response.json()
                return [
                    {
                        "name": repo["name"],
                        "description": repo["description"],
                        "html_url": repo["html_url"],
                        "language": repo["language"],
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"]
                    }
                    for repo in repos[:10]
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
        contact_messages = await read_json_file("contact_messages")
        projects = await read_json_file("projects")
        photography = await read_json_file("photography")
        education = await read_json_file("education")
        
        analytics = {
            "total_contacts": len(contact_messages),
            "total_projects": len(projects),
            "total_photos": len(photography),
            "total_education": len(education),
            "last_contact": contact_messages[-1]["timestamp"] if contact_messages else None,
            "most_recent_project": projects[-1]["created_at"] if projects else None,
            "most_recent_photo": photography[-1]["created_at"] if photography else None
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
    
    try:
        # Sample skills data
        skills_data = [
            {"id": str(uuid.uuid4()), "name": "JavaScript", "level": 95, "category": "Frontend", "icon": "🟨"},
            {"id": str(uuid.uuid4()), "name": "Python", "level": 90, "category": "Backend", "icon": "🐍"},
            {"id": str(uuid.uuid4()), "name": "React", "level": 92, "category": "Frontend", "icon": "⚛️"},
            {"id": str(uuid.uuid4()), "name": "FastAPI", "level": 88, "category": "Backend", "icon": "🚀"},
            {"id": str(uuid.uuid4()), "name": "MongoDB", "level": 85, "category": "Database", "icon": "🍃"},
            {"id": str(uuid.uuid4()), "name": "Photography", "level": 88, "category": "Creative", "icon": "📸"},
            {"id": str(uuid.uuid4()), "name": "UI/UX Design", "level": 85, "category": "Design", "icon": "🎨"},
            {"id": str(uuid.uuid4()), "name": "Node.js", "level": 83, "category": "Backend", "icon": "🟢"}
        ]
        
        # Sample projects data
        projects_data = [
            {
                "id": str(uuid.uuid4()),
                "title": "Neural Network Portfolio",
                "description": "Interactive portfolio with neural network background animations and particle effects",
                "technologies": ["React", "Canvas", "Neural Networks", "FastAPI"],
                "github_url": "https://github.com/sourabhkhairwal/neural-portfolio",
                "demo_url": "https://sourabhkhairwal-portfolio.com",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Photography Gallery System",
                "description": "Dynamic photography gallery with advanced slideshow and metadata display",
                "technologies": ["React", "Node.js", "Express", "MongoDB"],
                "github_url": "https://github.com/sourabhkhairwal/photo-gallery",
                "demo_url": "https://gallery.sourabhkhairwal.com",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Email Integration System",
                "description": "Professional contact form with Gmail SMTP integration and PDF resume generation",
                "technologies": ["FastAPI", "Gmail SMTP", "ReportLab", "React"],
                "github_url": "https://github.com/sourabhkhairwal/email-system",
                "demo_url": "https://contact.sourabhkhairwal.com",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        # Sample education data with certificate links
        education_data = [
            {
                "id": str(uuid.uuid4()),
                "degree": "Bachelor of Science in Computer Science",
                "school": "Tech University",
                "year": "2018 - 2022",
                "description": "Focused on software engineering, algorithms, and web development",
                "type": "education",
                "icon": "🎓",
                "certificate_url": None
            },
            {
                "id": str(uuid.uuid4()),
                "degree": "Master of Science in Software Engineering",
                "school": "Advanced Tech Institute",
                "year": "2022 - 2024",
                "description": "Specialized in full-stack development and system architecture",
                "type": "education",
                "icon": "📚",
                "certificate_url": None
            },
            {
                "id": str(uuid.uuid4()),
                "degree": "AWS Certified Developer",
                "school": "Amazon Web Services",
                "year": "2023",
                "description": "Cloud development and deployment certification",
                "type": "certification",
                "icon": "☁️",
                "certificate_url": "https://www.credly.com/badges/aws-certified-developer"
            },
            {
                "id": str(uuid.uuid4()),
                "degree": "React Advanced Certification",
                "school": "Meta",
                "year": "2023",
                "description": "Advanced React development and state management",
                "type": "certification",
                "icon": "⚛️",
                "certificate_url": "https://coursera.org/share/react-advanced-certification"
            },
            {
                "id": str(uuid.uuid4()),
                "degree": "Python Expert Certification",
                "school": "Python Institute",
                "year": "2022",
                "description": "Advanced Python programming and best practices",
                "type": "certification",
                "icon": "🐍",
                "certificate_url": "https://pythoninstitute.org/certification"
            },
            {
                "id": str(uuid.uuid4()),
                "degree": "Professional Photography Certificate",
                "school": "Photography Academy",
                "year": "2021",
                "description": "Advanced photography techniques and portfolio development",
                "type": "certification",
                "icon": "📸",
                "certificate_url": "https://photography-academy.com/certificates/professional"
            }
        ]
        
        # Sample photography data
        photography_data = [
            {
                "id": str(uuid.uuid4()),
                "title": "Coastal Majesty",
                "description": "Dramatic cliff formations meet the endless ocean in this breathtaking coastal landscape. Shot during golden hour to capture the warm light dancing on the rock formations.",
                "camera": "Canon EOS R5",
                "settings": "f/11, 1/60s, ISO 100",
                "location": "Big Sur, California",
                "image_url": "https://images.pexels.com/photos/3558637/pexels-photo-3558637.jpeg",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Mountain Reflection",
                "description": "Perfect symmetry captured in this serene mountain lake reflection. The stillness of the water creates a mirror-like surface that doubles the beauty of the landscape.",
                "camera": "Sony A7R IV",
                "settings": "f/8, 1/125s, ISO 200",
                "location": "Lake Louise, Canada",
                "image_url": "https://images.pexels.com/photos/2613946/pexels-photo-2613946.jpeg",
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
        
        existing_education = await read_json_file("education")
        if not existing_education:
            await write_json_file("education", education_data)
        
        existing_photography = await read_json_file("photography")
        if not existing_photography:
            await write_json_file("photography", photography_data)
        
        logger.info("Sample data initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing sample data: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Portfolio API shutting down...")
    client.close()

if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
