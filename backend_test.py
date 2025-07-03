#!/usr/bin/env python3
import requests
import json
import time
import os
import sys
from datetime import datetime

# Get the backend URL from the frontend .env file
def get_backend_url():
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                return line.strip().split('=')[1].strip('"\'')
    raise ValueError("REACT_APP_BACKEND_URL not found in frontend/.env")

# Base URL for API calls
BASE_URL = f"{get_backend_url()}/api"
print(f"Using backend URL: {BASE_URL}")

# Test results tracking
test_results = {
    "total_tests": 0,
    "passed_tests": 0,
    "failed_tests": 0,
    "test_details": []
}

def run_test(test_name, test_func):
    """Run a test and track results"""
    test_results["total_tests"] += 1
    print(f"\n{'='*80}\nRunning test: {test_name}\n{'='*80}")
    
    try:
        start_time = time.time()
        result = test_func()
        end_time = time.time()
        
        if result:
            test_results["passed_tests"] += 1
            status = "PASSED"
        else:
            test_results["failed_tests"] += 1
            status = "FAILED"
            
        test_results["test_details"].append({
            "name": test_name,
            "status": status,
            "duration": round(end_time - start_time, 2)
        })
        
        print(f"Test {status}: {test_name}")
        return result
    except Exception as e:
        test_results["failed_tests"] += 1
        test_results["test_details"].append({
            "name": test_name,
            "status": "ERROR",
            "error": str(e)
        })
        print(f"Test ERROR: {test_name}")
        print(f"Error: {str(e)}")
        return False

def test_root_endpoint():
    """Test the root API endpoint for health check"""
    response = requests.get(f"{BASE_URL}/")
    
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        return False
    
    data = response.json()
    if "message" not in data or "status" not in data:
        print(f"Error: Response missing expected fields: {data}")
        return False
        
    if data["message"] != "Portfolio API is running" or data["status"] != "healthy":
        print(f"Error: Unexpected response content: {data}")
        return False
        
    print("Root endpoint health check successful")
    return True

def test_json_storage_contact():
    """Test JSON storage for contact messages"""
    # Create a test contact message
    test_data = {
        "name": "Test User",
        "email": "test@example.com",
        "message": "This is a test message from the automated test suite."
    }
    
    # Submit the contact message
    response = requests.post(f"{BASE_URL}/contact", json=test_data)
    
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    data = response.json()
    if "message" not in data or "id" not in data:
        print(f"Error: Response missing expected fields: {data}")
        return False
    
    message_id = data["id"]
    print(f"Contact message created with ID: {message_id}")
    
    # Verify the message was stored by retrieving all messages
    response = requests.get(f"{BASE_URL}/contact")
    
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        return False
    
    messages = response.json()
    if not isinstance(messages, list):
        print(f"Error: Expected a list of messages, got {type(messages)}")
        return False
    
    # Find our test message
    found = False
    for msg in messages:
        if msg.get("id") == message_id:
            found = True
            if msg["name"] != test_data["name"] or msg["email"] != test_data["email"] or msg["message"] != test_data["message"]:
                print(f"Error: Retrieved message data doesn't match submitted data: {msg}")
                return False
            break
    
    if not found:
        print(f"Error: Couldn't find the submitted message with ID {message_id} in the retrieved messages")
        return False
    
    print("JSON storage for contact messages working correctly")
    return True

def test_json_storage_projects():
    """Test JSON storage for projects"""
    # Create a test project
    test_data = {
        "title": "Test Project",
        "description": "This is a test project created by the automated test suite.",
        "technologies": ["Python", "FastAPI", "Testing"],
        "github_url": "https://github.com/test/test-project",
        "demo_url": "https://test-project.example.com"
    }
    
    # Submit the project
    response = requests.post(f"{BASE_URL}/projects", json=test_data)
    
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    data = response.json()
    if "message" not in data or "id" not in data:
        print(f"Error: Response missing expected fields: {data}")
        return False
    
    project_id = data["id"]
    print(f"Project created with ID: {project_id}")
    
    # Verify the project was stored by retrieving all projects
    response = requests.get(f"{BASE_URL}/projects")
    
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        return False
    
    projects = response.json()
    if not isinstance(projects, list):
        print(f"Error: Expected a list of projects, got {type(projects)}")
        return False
    
    # Find our test project
    found = False
    for project in projects:
        if project.get("id") == project_id:
            found = True
            if (project["title"] != test_data["title"] or 
                project["description"] != test_data["description"] or 
                project["technologies"] != test_data["technologies"]):
                print(f"Error: Retrieved project data doesn't match submitted data: {project}")
                return False
            break
    
    if not found:
        print(f"Error: Couldn't find the submitted project with ID {project_id} in the retrieved projects")
        return False
    
    print("JSON storage for projects working correctly")
    return True

def test_json_storage_skills():
    """Test JSON storage for skills"""
    # Create a test skill
    test_data = {
        "name": "Test Skill",
        "level": 85,
        "category": "Testing",
        "icon": "🧪"
    }
    
    # Submit the skill
    response = requests.post(f"{BASE_URL}/skills", json=test_data)
    
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    data = response.json()
    if "message" not in data or "id" not in data:
        print(f"Error: Response missing expected fields: {data}")
        return False
    
    skill_id = data["id"]
    print(f"Skill created with ID: {skill_id}")
    
    # Verify the skill was stored by retrieving all skills
    response = requests.get(f"{BASE_URL}/skills")
    
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        return False
    
    skills = response.json()
    if not isinstance(skills, list):
        print(f"Error: Expected a list of skills, got {type(skills)}")
        return False
    
    # Find our test skill
    found = False
    for skill in skills:
        if skill.get("id") == skill_id:
            found = True
            if (skill["name"] != test_data["name"] or 
                skill["level"] != test_data["level"] or 
                skill["category"] != test_data["category"]):
                print(f"Error: Retrieved skill data doesn't match submitted data: {skill}")
                return False
            break
    
    if not found:
        print(f"Error: Couldn't find the submitted skill with ID {skill_id} in the retrieved skills")
        return False
    
    print("JSON storage for skills working correctly")
    return True

def test_weather_api():
    """Test the weather API endpoint"""
    response = requests.get(f"{BASE_URL}/weather")
    
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        return False
    
    data = response.json()
    required_fields = ["location", "temperature", "description", "icon"]
    
    for field in required_fields:
        if field not in data:
            print(f"Error: Weather data missing required field '{field}'")
            return False
    
    print(f"Weather API returned data for {data['location']}: {data['temperature']}, {data['description']} {data['icon']}")
    return True

def test_github_api():
    """Test the GitHub API integration"""
    # Test with a known GitHub username
    username = "octocat"
    response = requests.get(f"{BASE_URL}/github/{username}")
    
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        return False
    
    repos = response.json()
    if not isinstance(repos, list):
        print(f"Error: Expected a list of repositories, got {type(repos)}")
        return False
    
    if len(repos) == 0:
        print(f"Warning: No repositories returned for user '{username}'")
        # This might be expected if the user has no public repos
        # We'll still pass the test but with a warning
    else:
        # Check the structure of the first repo
        repo = repos[0]
        required_fields = ["name", "description", "html_url", "language", "stars", "forks"]
        
        for field in required_fields:
            if field not in repo:
                print(f"Error: Repository data missing required field '{field}'")
                return False
        
        print(f"GitHub API returned {len(repos)} repositories for user '{username}'")
        print(f"First repo: {repo['name']} - {repo['description']}")
    
    return True

def test_analytics_api():
    """Test the analytics API endpoint"""
    response = requests.get(f"{BASE_URL}/analytics")
    
    if response.status_code != 200:
        print(f"Error: Expected status code 200, got {response.status_code}")
        return False
    
    data = response.json()
    required_fields = ["total_contacts", "total_projects"]
    
    for field in required_fields:
        if field not in data:
            print(f"Error: Analytics data missing required field '{field}'")
            return False
    
    print(f"Analytics API returned data: {data}")
    return True

def run_all_tests():
    """Run all tests and print a summary"""
    print(f"\n{'='*80}\nStarting Portfolio Backend API Tests\n{'='*80}")
    print(f"Testing backend at: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    run_test("Root Endpoint Health Check", test_root_endpoint)
    run_test("JSON Storage - Contact Messages", test_json_storage_contact)
    run_test("JSON Storage - Projects", test_json_storage_projects)
    run_test("JSON Storage - Skills", test_json_storage_skills)
    run_test("Weather API", test_weather_api)
    run_test("GitHub API Integration", test_github_api)
    run_test("Analytics API", test_analytics_api)
    
    # Print summary
    print(f"\n{'='*80}\nTest Summary\n{'='*80}")
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"Passed: {test_results['passed_tests']}")
    print(f"Failed: {test_results['failed_tests']}")
    print(f"Success Rate: {(test_results['passed_tests'] / test_results['total_tests']) * 100:.2f}%")
    
    # Print details of failed tests
    if test_results['failed_tests'] > 0:
        print(f"\nFailed Tests:")
        for test in test_results['test_details']:
            if test['status'] != 'PASSED':
                print(f"  - {test['name']}: {test['status']}")
                if 'error' in test:
                    print(f"    Error: {test['error']}")
    
    return test_results['failed_tests'] == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)