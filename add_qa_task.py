#!/usr/bin/env python3
"""
Simple script to add test tasks to QA section for testing the Asana agent.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if not os.getenv('ASANA_API_KEY'):
    print("❌ ERROR: ASANA_API_KEY not found!")
    print("📝 Please set your Asana API key in the .env file")
    exit(1)

if not os.getenv('ASANA_PROJECT_ID'):
    print("❌ ERROR: ASANA_PROJECT_ID not found!")
    print("📝 Please set your Asana project ID in the .env file")
    exit(1)

from asana import Client

def add_test_task(name, notes):
    """Add a test task to QA section."""
    try:
        client = Client.access_token(os.getenv('ASANA_API_KEY'))
        project_id = os.getenv('ASANA_PROJECT_ID')
        
        # Get QA section
        sections = client.sections.find_by_project(project_id)
        qa_section = None
        
        for section in sections:
            if section.get('name', '').lower() == 'qa':
                qa_section = section
                break
        
        if not qa_section:
            print("❌ QA section not found!")
            return False
        
        # Create task in QA section
        task_data = {
            'name': name,
            'notes': notes,
            'projects': [project_id],
            'memberships': [{'project': project_id, 'section': qa_section.get('gid')}]
        }
        
        task = client.tasks.create(task_data)
        print(f"✅ Created task: {task.get('name')} (ID: {task.get('gid')})")
        return True
        
    except Exception as e:
        print(f"❌ Error creating task: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Adding test tasks to QA section...")
    print("=" * 50)
    
    # Example test tasks
    test_tasks = [
        {
            "name": "Test Form 471 with PDF URL",
            "notes": "This task contains a Form 471 PDF URL for testing.\n\nForm 471 URL: http://publicdata.usac.org/SL/Prd/Form471/332726/251043327/Original/USAC_FCC_FORM_471_APPLICATION_251043327_CERTIFIED.pdf"
        },
        {
            "name": "Test No PDF Available",
            "notes": "This task has no PDF attachments or URLs for testing the no-PDF scenario."
        },
        {
            "name": "Test Invalid PDF URL",
            "notes": "This task has an invalid PDF URL for testing error handling.\n\nInvalid URL: http://example.com/invalid.pdf"
        }
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n📝 Adding test task {i}/3...")
        add_test_task(task["name"], task["notes"])
    
    print("\n✅ All test tasks added!")
    print("🔄 You can now run the agent to process these tasks:")
    print("   python3 asana_form_agent.py --watcher") 