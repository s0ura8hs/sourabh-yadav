import React, { useEffect, useRef, useState } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Neural Network Background Component
const NeuralNetworkBackground = () => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const nodesRef = useRef([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    class Node {
      constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = (Math.random() - 0.5) * 0.5;
        this.energy = Math.random();
        this.pulse = Math.random() * Math.PI * 2;
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;
        this.pulse += 0.02;
        this.energy = Math.abs(Math.sin(this.pulse));

        if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
        if (this.y < 0 || this.y > canvas.height) this.vy *= -1;

        this.x = Math.max(0, Math.min(canvas.width, this.x));
        this.y = Math.max(0, Math.min(canvas.height, this.y));
      }

      draw(ctx) {
        ctx.save();
        ctx.globalAlpha = this.energy * 0.8 + 0.2;
        
        const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, 8);
        gradient.addColorStop(0, `rgba(100, 200, 255, ${this.energy})`);
        gradient.addColorStop(0.5, `rgba(50, 150, 255, ${this.energy * 0.5})`);
        gradient.addColorStop(1, 'rgba(0, 100, 255, 0)');
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(this.x, this.y, 8, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.restore();
      }
    }

    const nodeCount = 50;
    nodesRef.current = [];
    for (let i = 0; i < nodeCount; i++) {
      nodesRef.current.push(new Node(
        Math.random() * canvas.width,
        Math.random() * canvas.height
      ));
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      nodesRef.current.forEach(node => {
        node.update();
        node.draw(ctx);
      });

      ctx.strokeStyle = 'rgba(100, 200, 255, 0.3)';
      ctx.lineWidth = 1;
      
      for (let i = 0; i < nodesRef.current.length; i++) {
        for (let j = i + 1; j < nodesRef.current.length; j++) {
          const nodeA = nodesRef.current[i];
          const nodeB = nodesRef.current[j];
          const distance = Math.sqrt(
            Math.pow(nodeA.x - nodeB.x, 2) + Math.pow(nodeA.y - nodeB.y, 2)
          );

          if (distance < 150) {
            const opacity = (150 - distance) / 150;
            const energy = (nodeA.energy + nodeB.energy) / 2;
            
            ctx.save();
            ctx.globalAlpha = opacity * energy * 0.5;
            ctx.strokeStyle = `rgba(100, 200, 255, ${opacity * energy})`;
            ctx.lineWidth = energy * 2;
            
            ctx.beginPath();
            ctx.moveTo(nodeA.x, nodeA.y);
            
            const midX = (nodeA.x + nodeB.x) / 2 + (Math.random() - 0.5) * 10;
            const midY = (nodeA.y + nodeB.y) / 2 + (Math.random() - 0.5) * 10;
            
            ctx.quadraticCurveTo(midX, midY, nodeB.x, nodeB.y);
            ctx.stroke();
            
            ctx.restore();
          }
        }
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 z-0"
      style={{ 
        background: 'radial-gradient(ellipse at center, #001122 0%, #000000 70%)',
        opacity: 0.4
      }}
    />
  );
};

// Particle System Component
const ParticleSystem = () => {
  const canvasRef = useRef(null);
  const particlesRef = useRef([]);
  const animationRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    class Particle {
      constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 2;
        this.vy = (Math.random() - 0.5) * 2;
        this.life = 1;
        this.decay = Math.random() * 0.02 + 0.01;
        this.size = Math.random() * 3 + 1;
        this.sparkle = Math.random() * 2 * Math.PI;
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;
        this.life -= this.decay;
        this.sparkle += 0.1;
        this.size *= 0.99;
      }

      draw(ctx) {
        ctx.save();
        ctx.globalAlpha = this.life;
        
        const gradient = ctx.createRadialGradient(
          this.x, this.y, 0,
          this.x, this.y, this.size * 4
        );
        
        const brightness = Math.abs(Math.sin(this.sparkle));
        gradient.addColorStop(0, `rgba(255, 255, 255, ${brightness})`);
        gradient.addColorStop(0.5, `rgba(192, 192, 192, ${brightness * 0.7})`);
        gradient.addColorStop(1, `rgba(128, 128, 128, 0)`);
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.strokeStyle = `rgba(255, 255, 255, ${brightness})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(this.x - this.size, this.y);
        ctx.lineTo(this.x + this.size, this.y);
        ctx.moveTo(this.x, this.y - this.size);
        ctx.lineTo(this.x, this.y + this.size);
        ctx.stroke();
        
        ctx.restore();
      }
    }

    const handleMouseMove = (e) => {
      for (let i = 0; i < 3; i++) {
        particlesRef.current.push(
          new Particle(
            e.clientX + (Math.random() - 0.5) * 20,
            e.clientY + (Math.random() - 0.5) * 20
          )
        );
      }
    };

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      particlesRef.current = particlesRef.current.filter(particle => {
        particle.update();
        particle.draw(ctx);
        return particle.life > 0 && particle.size > 0.1;
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    document.addEventListener('mousemove', handleMouseMove);
    animate();

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', resizeCanvas);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-10"
      style={{ mixBlendMode: 'screen' }}
    />
  );
};

// Navigation Component
const Navigation = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setIsMenuOpen(false);
  };

  const downloadResume = async () => {
    try {
      const response = await axios.get(`${API}/resume/generate`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'Sourabh_Khairwal_Resume.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading resume:', error);
      alert('Error downloading resume. Please try again.');
    }
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-black/20 backdrop-blur-md border-b border-gray-800/30">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="text-2xl font-bold bg-gradient-to-r from-blue-200 to-blue-400 bg-clip-text text-transparent">
            Sourabh Portfolio
          </div>
          
          <div className="hidden md:flex space-x-8 items-center">
            {['home', 'about', 'skills', 'education', 'photography', 'projects', 'contact'].map((item) => (
              <button
                key={item}
                onClick={() => scrollToSection(item)}
                className="text-gray-300 hover:text-white transition-colors duration-300 capitalize relative group"
              >
                {item}
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-300 to-blue-500 transition-all duration-300 group-hover:w-full"></span>
              </button>
            ))}
            
            <button
              onClick={downloadResume}
              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg font-semibold hover:from-blue-500 hover:to-blue-600 transition-all duration-300 transform hover:scale-105"
            >
              📄 Download Resume
            </button>
          </div>

          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden text-gray-300 hover:text-white transition-colors duration-300"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>

        {isMenuOpen && (
          <div className="md:hidden mt-4 py-4 border-t border-gray-800/30">
            {['home', 'about', 'skills', 'education', 'photography', 'projects', 'contact'].map((item) => (
              <button
                key={item}
                onClick={() => scrollToSection(item)}
                className="block w-full text-left px-4 py-2 text-gray-300 hover:text-white transition-colors duration-300 capitalize"
              >
                {item}
              </button>
            ))}
            <button
              onClick={downloadResume}
              className="block w-full text-left px-4 py-2 text-blue-300 hover:text-white transition-colors duration-300"
            >
              📄 Download Resume
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};

// Hero Section
const HeroSection = () => {
  return (
    <section id="home" className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-black/60 via-gray-900/40 to-black/60" />
      
      <div className="relative z-20 text-center px-6">
        <h1 className="text-6xl md:text-8xl font-bold mb-6 bg-gradient-to-r from-blue-200 via-white to-blue-300 bg-clip-text text-transparent animate-pulse">
          Sourabh 
        </h1>
        <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-2xl mx-auto">
          Full stack learner
        </p>
        <p className="text-lg text-gray-400 mb-12 max-w-3xl mx-auto">
          Crafting digital experiences with interactive effects and cutting-edge technologies
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button 
            onClick={() => document.getElementById('projects').scrollIntoView({ behavior: 'smooth' })}
            className="px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-lg font-semibold hover:from-blue-500 hover:to-blue-700 transition-all duration-300 transform hover:scale-105"
          >
            View My Work
          </button>
          <button 
            onClick={() => document.getElementById('contact').scrollIntoView({ behavior: 'smooth' })}
            className="px-8 py-3 border-2 border-blue-600 text-blue-300 rounded-lg font-semibold hover:bg-blue-600 hover:text-white transition-all duration-300"
          >
            Get In Touch
          </button>
        </div>
      </div>
    </section>
  );
};

// About Section
const AboutSection = () => {
  return (
    <section id="about" className="py-20 px-6 relative">
      <div className="container mx-auto max-w-6xl">
        <h2 className="text-4xl md:text-5xl font-bold text-center mb-16 bg-gradient-to-r from-blue-200 to-blue-400 bg-clip-text text-transparent">
          About Me
        </h2>
        
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h3 className="text-2xl font-semibold text-gray-200 mb-6">
              Passionate Developer & Creative Photographer
            </h3>
            <p className="text-gray-400 mb-6 leading-relaxed">
              I'm a full-stack developer who believes in creating not just functional applications, 
              but digital experiences that captivate and inspire. With expertise in modern web technologies 
              and a keen eye for interactive design, I bring ideas to life through code.
            </p>
            <p className="text-gray-400 mb-6 leading-relaxed">
              Beyond coding, I'm passionate about photography, capturing moments that tell stories 
              and exploring the intersection of technology and art. This creative perspective enhances 
              my approach to software development and user experience design.
            </p>
            
            <div className="flex flex-wrap gap-3">
              {['JavaScript', 'React', 'C/C++' , 'Java' , 'Python', 'FastAPI', 'Photography', 'UI/UX'].map((tech) => (
                <span 
                  key={tech}
                  className="px-4 py-2 bg-gradient-to-r from-blue-800 to-blue-700 text-blue-200 rounded-full text-sm font-medium hover:from-blue-700 hover:to-blue-600 transition-all duration-300"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>
          
         <div className="relative">
            <div className="w-full h-96 bg-gradient-to-br from-blue-900/50 to-gray-900/50 rounded-lg overflow-hidden relative border border-blue-800/30">
              <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-blue-600/20 to-transparent animate-pulse"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <img 
                  src="/path/to/your/image.jpg" 
                  alt="Your Name - Developer and Photographer"
                  className="w-full h-full object-cover rounded-lg"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// Skills Section
const SkillsSection = () => {
  const skills = [
    { name: 'Frontend Development', level: 95, icon: '♨️' },
    { name: 'Backend Development', level: 90, icon: '⚙️' },
    { name: 'Database Design', level: 85, icon: '💾' },
    { name: 'API Integration', level: 92, icon: '🔗' },
    { name: 'Photography', level: 88, icon: '📸' },
    { name: 'UI/UX Design', level: 85, icon: '✨' },
   { name: 'Database Design', level: 85, icon: '💾' },
    { name: 'API Integration', level: 92, icon: '🔗' },
    { name: 'Photography', level: 88, icon: '📸' },
    { name: 'UI/UX Design', level: 85, icon: '✨' },
  ];

  return (
    <section id="skills" className="py-20 px-6 bg-gradient-to-b from-blue-900/20 to-transparent">
      <div className="container mx-auto max-w-6xl">
        <h2 className="text-4xl md:text-5xl font-bold text-center mb-16 bg-gradient-to-r from-blue-200 to-blue-400 bg-clip-text text-transparent">
          Skills & Expertise
        </h2>
        
        <div className="grid md:grid-cols-2 gap-8">
          {skills.map((skill, index) => (
            <div key={index} className="group">
              <div className="flex items-center mb-3">
                <span className="text-2xl mr-3">{skill.icon}</span>
                <span className="text-gray-300 font-medium">{skill.name}</span>
                <span className="ml-auto text-gray-400 text-sm">{skill.level}%</span>
              </div>
              <div className="w-full bg-gray-800 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-blue-400 to-blue-600 h-2 rounded-full transition-all duration-1000 group-hover:from-blue-300 group-hover:to-blue-500"
                  style={{ width: `${skill.level}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Fixed Education Section
const EducationSection = () => {
  const [educationData, setEducationData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Define API URL explicitly
  const API_URL = process.env.REACT_APP_API_URL || 'https://sourabh-yadav.onrender.com/api';

  useEffect(() => {
    const fetchEducation = async () => {
      try {
        console.log('Fetching from URL:', `${API_URL}/education`);
        
        const response = await axios.get(`${API_URL}/education`, {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 10000, // 10 second timeout
        });
        
        console.log('Response received:', response.data);
        setEducationData(response.data);
        setError(null);
      } catch (error) {
        console.error('Detailed error:', error);
        console.error('Error response:', error.response);
        console.error('Error message:', error.message);
        
        if (error.code === 'ECONNABORTED') {
          setError('Request timeout - server may be slow');
        } else if (error.response) {
          setError(`Server error: ${error.response.status}`);
        } else if (error.request) {
          setError('Network error - cannot reach server');
        } else {
          setError(error.message);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchEducation();
  }, [API_URL]);

  const education = educationData.filter(item => item.type === 'education');
  const certificates = educationData.filter(item => item.type === 'certification');

  if (loading) {
    return (
      <section id="education" className="py-20 px-6 relative">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center text-gray-400">Loading education data...</div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section id="education" className="py-20 px-6 relative">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center">
            <div className="text-red-400 mb-4">Error loading education data: {error}</div>
            <div className="text-gray-400 text-sm">
              Trying to fetch from: {API_URL}/education
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section id="education" className="py-20 px-6 relative">
      <div className="container mx-auto max-w-6xl">
        <h2 className="text-4xl md:text-5xl font-bold text-center mb-16 bg-gradient-to-r from-blue-200 to-blue-400 bg-clip-text text-transparent">
          Education & Certifications
        </h2>
        
        <div className="grid lg:grid-cols-2 gap-12">
          {/* Education */}
          <div>
            <h3 className="text-2xl font-semibold text-gray-200 mb-8 flex items-center">
              <span className="text-3xl mr-3">🎓</span>
              Education
            </h3>
            
            <div className="space-y-6">
              {education.map((edu) => (
                <div key={edu.id} className="bg-gradient-to-r from-blue-900/20 to-gray-900/20 rounded-lg p-6 border border-blue-800/30 hover:border-blue-600/50 transition-all duration-300">
                  <div className="flex items-start">
                    <span className="text-3xl mr-4">{edu.icon}</span>
                    <div className="flex-1">
                      <h4 className="text-xl font-semibold text-gray-200 mb-2">{edu.degree}</h4>
                      <p className="text-blue-300 font-medium mb-2">{edu.school}</p>
                      <p className="text-gray-400 text-sm mb-3">{edu.year}</p>
                      <p className="text-gray-400 text-sm">{edu.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Certifications */}
          <div>
            <h3 className="text-2xl font-semibold text-gray-200 mb-8 flex items-center">
              <span className="text-3xl mr-3">🏆</span>
              Certifications
            </h3>
            
            <div className="space-y-4">
              {certificates.map((cert) => (
                <div key={cert.id} className="bg-gradient-to-r from-blue-900/20 to-gray-900/20 rounded-lg p-4 border border-blue-800/30 hover:border-blue-600/50 transition-all duration-300">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center flex-1">
                      <span className="text-2xl mr-4">{cert.icon}</span>
                      <div className="flex-1">
                        <h4 className="text-lg font-semibold text-gray-200">{cert.degree}</h4>
                        <p className="text-blue-300 text-sm">{cert.school}</p>
                      </div>
                      <span className="text-gray-400 text-sm mr-4">{cert.year}</span>
                    </div>
                    
                    {cert.certificate_url && (
                      <a 
                        href={cert.certificate_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white text-xs rounded-full transition-colors duration-300 flex items-center"
                      >
                        🔗 View Certificate
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
// Photography Section
const PhotographySection = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [imageLoaded, setImageLoaded] = useState(false);
  
  const photographs = [
    {
      id: 1,
      url: "frontend/src/images/9.jpg",
      title: "Coastal Majesty",
      description: "Dramatic cliff formations meet the endless ocean in this breathtaking coastal landscape. Shot during golden hour to capture the warm light dancing on the rock formations.",
      camera: "Canon EOS R5",
      settings: "f/11, 1/60s, ISO 100",
      location: "Big Sur, California"
    },
    {
      id: 2,
      url: "frontend/src/images/6.jpg",
      title: "Mountain Reflection",
      description: "Perfect symmetry captured in this serene mountain lake reflection. The stillness of the water creates a mirror-like surface that doubles the beauty of the landscape.",
      camera: "Sony A7R IV",
      settings: "f/8, 1/125s, ISO 200",
      location: "Lake Louise, Canada"
    },
    {
      id: 3,
      url: "frontend/src/images/8.jpg",
      title: "Aerial Perspective",
      description: "A winding river cuts through the mountainous landscape, creating natural patterns that can only be fully appreciated from above. This aerial shot showcases the intricate relationship between water and land.",
      camera: "DJI Mavic 3",
      settings: "f/5.6, 1/200s, ISO 100",
      location: "Norwegian Fjords"
    },
    {
      id: 4,
      url: "frontend/src/images/7.jpg",
      title: "Alpine Serenity",
      description: "The turquoise waters of this alpine lake create a striking contrast against the snow-capped peaks. The unique color comes from glacial sediment suspended in the water.",
      camera: "Nikon Z9",
      settings: "f/9, 1/90s, ISO 64",
      location: "Swiss Alps"
    },
    {
      id: 5,
      url: "frontend/src/images/3.jpg",
      title: "Behind the Lens",
      description: "A glimpse into the photographer's world - equipment, planning, and the tools that help capture these moments. This workspace represents the technical side of creative photography.",
      camera: "iPhone 14 Pro",
      settings: "Portrait mode, f/1.8",
      location: "Home Studio"
    }
  ];

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % photographs.length);
    setImageLoaded(false);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + photographs.length) % photographs.length);
    setImageLoaded(false);
  };

  const handleImageLoad = () => {
    setImageLoaded(true);
  };

  const currentPhoto = photographs[currentSlide];

  return (
    <section id="photography" className="py-20 px-6 bg-gradient-to-b from-blue-900/20 to-transparent">
      <div className="container mx-auto max-w-6xl">
        <h2 className="text-4xl md:text-5xl font-bold text-center mb-16 bg-gradient-to-r from-blue-200 to-blue-400 bg-clip-text text-transparent">
          Photography Portfolio
        </h2>
        
        <div className="relative max-w-4xl mx-auto">
          <div className="relative flex justify-center items-center min-h-[400px] rounded-lg overflow-hidden bg-gradient-to-br from-blue-900/50 to-gray-900/50 border border-blue-800/30">
            <img 
              src={currentPhoto.url} 
              alt={currentPhoto.title}
              className={`max-w-full max-h-[70vh] w-auto h-auto object-contain transition-opacity duration-500 ${
                imageLoaded ? 'opacity-100' : 'opacity-0'
              }`}
              onLoad={handleImageLoad}
            />
            
            {/* Loading placeholder */}
            {!imageLoaded && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
              </div>
            )}
            
            <button
              onClick={prevSlide}
              className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white p-3 rounded-full transition-all duration-300 z-10"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            
            <button
              onClick={nextSlide}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white p-3 rounded-full transition-all duration-300 z-10"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <div className="mt-8 bg-gradient-to-r from-blue-900/20 to-gray-900/20 rounded-lg p-6 border border-blue-800/30">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-2xl font-bold text-gray-200 mb-3">{currentPhoto.title}</h3>
                <p className="text-gray-400 mb-4 leading-relaxed">{currentPhoto.description}</p>
                <div className="flex items-center text-blue-300 text-sm">
                  <span className="mr-2">📍</span>
                  <span>{currentPhoto.location}</span>
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center">
                  <span className="text-blue-300 font-medium w-20">Camera:</span>
                  <span className="text-gray-400">{currentPhoto.camera}</span>
                </div>
                <div className="flex items-center">
                  <span className="text-blue-300 font-medium w-20">Settings:</span>
                  <span className="text-gray-400">{currentPhoto.settings}</span>
                </div>
                <div className="flex items-center">
                  <span className="text-blue-300 font-medium w-20">Location:</span>
                  <span className="text-gray-400">{currentPhoto.location}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-center mt-6 space-x-2">
            {photographs.map((_, index) => (
              <button
                key={index}
                onClick={() => {
                  setCurrentSlide(index);
                  setImageLoaded(false);
                }}
                className={`w-3 h-3 rounded-full transition-all duration-300 ${
                  index === currentSlide 
                    ? 'bg-blue-500 scale-125' 
                    : 'bg-gray-600 hover:bg-gray-500'
                }`}
              />
            ))}
          </div>
          
          <div className="text-center mt-4 text-gray-400 text-sm">
            {currentSlide + 1} / {photographs.length}
          </div>
        </div>
      </div>
    </section>
  );
};
// Projects Section
const ProjectsSection = () => {
  const projects = [
    {
      title: 'Neural Network Portfolio',
      description: 'This very portfolio showcasing advanced animations and interactive effects',
      tech: ['React', 'Canvas', 'Neural Networks', 'Particle Systems'],
      image: 'https://images.unsplash.com/photo-1518186233392-c232efbf2373?w=400&h=300&fit=crop',
      demo: '#',
      github: '#'
    },
    {
      title: 'Interactive Data Visualization',
      description: 'Real-time data visualization dashboard with interactive charts and animations',
      tech: ['React', 'D3.js', 'Python', 'FastAPI'],
      image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop',
      demo: '#',
      github: '#'
    },
    {
      title: 'Photography Gallery App',
      description: 'Dynamic photo gallery with advanced slideshow and metadata display',
      tech: ['React', 'Node.js', 'Express', 'MongoDB'],
      image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=300&fit=crop',
      demo: '#',
      github: '#'
    }
  ];

  return (
    <section id="projects" className="py-20 px-6">
      <div className="container mx-auto max-w-6xl">
        <h2 className="text-4xl md:text-5xl font-bold text-center mb-16 bg-gradient-to-r from-blue-200 to-blue-400 bg-clip-text text-transparent">
          Featured Projects
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {projects.map((project, index) => (
            <div key={index} className="group relative overflow-hidden rounded-lg bg-gradient-to-br from-blue-900/30 to-gray-900/30 hover:from-blue-800/40 hover:to-gray-800/40 transition-all duration-300 transform hover:scale-105 border border-blue-800/30 hover:border-blue-600/50">
              <div className="aspect-video overflow-hidden">
                <img 
                  src={project.image} 
                  alt={project.title}
                  className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                />
              </div>
              
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-200 mb-3">{project.title}</h3>
                <p className="text-gray-400 mb-4 text-sm">{project.description}</p>
                
                <div className="flex flex-wrap gap-2 mb-4">
                  {project.tech.map((tech, techIndex) => (
                    <span 
                      key={techIndex}
                      className="px-2 py-1 bg-blue-900/50 text-blue-300 rounded text-xs border border-blue-800/30"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
                
                <div className="flex gap-3">
                  <a 
                    href={project.demo}
                    className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded text-sm hover:from-blue-500 hover:to-blue-600 transition-all duration-300"
                  >
                    Live Demo
                  </a>
                  <a 
                    href={project.github}
                    className="px-4 py-2 border border-blue-600 text-blue-300 rounded text-sm hover:bg-blue-600 hover:text-white transition-all duration-300"
                  >
                    GitHub
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Contact Section with Email Integration
const ContactSection = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus('');
    
    try {
      const response = await axios.post(`${API}/contact`, formData);
      
      if (response.data.email_sent) {
        setSubmitStatus('✅ Message sent successfully! You will receive a confirmation email.');
      } else {
        setSubmitStatus('✅ Message sent successfully! (Note: Email notification not configured)');
      }
      
      setFormData({ name: '', email: '', message: '' });
    } catch (error) {
      console.error('Error sending message:', error);
      setSubmitStatus('❌ Error sending message. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <section id="contact" className="py-20 px-6 bg-gradient-to-b from-blue-900/20 to-black/50">
      <div className="container mx-auto max-w-4xl">
        <h2 className="text-4xl md:text-5xl font-bold text-center mb-16 bg-gradient-to-r from-blue-200 to-blue-400 bg-clip-text text-transparent">
          Get In Touch
        </h2>
        
        <div className="grid md:grid-cols-2 gap-12">
          <div>
            <h3 className="text-2xl font-semibold text-gray-200 mb-6">Let's Create Something Amazing</h3>
            <p className="text-gray-400 mb-8 leading-relaxed">
              I'm always excited to work on new projects and collaborate with fellow creators. 
              Whether you have a project in mind or just want to say hello, I'd love to hear from you.
            </p>
            
            <div className="space-y-4">
              <div className="flex items-center">
                <span className="text-2xl mr-4">📧</span>
                <span className="text-gray-300">sourabhkhairwal@gmail.com</span>
              </div>
              <div className="flex items-center">
                <span className="text-2xl mr-4">🌐</span>
                <span className="text-gray-300">github.com/s0ura8hs</span>
              </div>
              <div className="flex items-center">
                <span className="text-2xl mr-4">💼</span>
                <span className="text-gray-300">linkedin.com/in/sourabh-khairwal</span>
              </div>
            </div>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Your Name"
                required
                className="w-full px-4 py-3 bg-blue-900/20 border border-blue-800/30 rounded-lg text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
              />
            </div>
            
            <div>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Your Email"
                required
                className="w-full px-4 py-3 bg-blue-900/20 border border-blue-800/30 rounded-lg text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
              />
            </div>
            
            <div>
              <textarea
                name="message"
                value={formData.message}
                onChange={handleChange}
                placeholder="Your Message"
                rows="6"
                required
                className="w-full px-4 py-3 bg-blue-900/20 border border-blue-800/30 rounded-lg text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600 resize-none"
              ></textarea>
            </div>
            
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-lg font-semibold hover:from-blue-500 hover:to-blue-700 transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {isSubmitting ? 'Sending...' : 'Send Message'}
            </button>
            
            {submitStatus && (
              <div className="text-center mt-4 p-3 rounded-lg bg-blue-900/20 border border-blue-800/30">
                <p className="text-sm">{submitStatus}</p>
              </div>
            )}
          </form>
        </div>
      </div>
    </section>
  );
};

// Weather Widget
const WeatherWidget = () => {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const response = await axios.get(`${API}/weather`);
        setWeather(response.data);
      } catch (error) {
        console.error('Error fetching weather:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchWeather();
  }, []);

  if (loading) {
    return (
      <div className="fixed bottom-4 right-4 bg-blue-900/50 backdrop-blur-sm rounded-lg p-4 text-white-300 animate-pulse border border-blue-800/30">
        Loading weather...
      </div>
    );
  }

  if (!weather) return null;

  return (
    <div className="fixed bottom-8 right-4 bg-blue-900/50 backdrop-blur-sm rounded-lg p-4 text-white-300 border border-blue-800/30">
      <div className="flex items-center space-x-3">
        <span className="text-2xl">{weather.icon || '🌤️'}</span>
        <div>
          <div className="font-semibold">{weather.location || 'New York'}</div>
          <div className="text-sm text-white-400">{weather.temperature || '22°C'}</div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="min-h-screen bg-black text-white overflow-x-hidden relative">
      <NeuralNetworkBackground />
      <ParticleSystem />
      <Navigation />
      <HeroSection />
      <AboutSection />
      <SkillsSection />
      <EducationSection />
      <PhotographySection />
      <ProjectsSection />
      <ContactSection />
      <WeatherWidget />
    </div>
  );
}

export default App;
