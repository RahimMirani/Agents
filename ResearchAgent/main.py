import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    
    # Check if required API key is set
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file")
        print("Please add your Google API key to the .env file:")
        print("GEMINI_API_KEY=your_api_key_here")
        return False
    return True

def setup_gemini():
    """Initialize Google Gemini AI model"""
    try:
        # Initialize Gemini model
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.3,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        return llm
    except Exception as e:
        print(f"❌ Error setting up Gemini: {e}")
        return None

def get_person_info():
    """Get person information from user input"""
    print("\n🔍 Person Research Agent")
    print("=" * 40)
    
    name = input("Enter the person's name: ").strip()
    if not name:
        print("❌ Name cannot be empty!")
        return None
    
    # Optional additional info
    print("\nOptional additional information (press Enter to skip):")
    company = input("Company/Organization: ").strip()
    location = input("Location: ").strip()
    profession = input("Profession: ").strip()
    
    person_info = {
        "name": name,
        "company": company if company else None,
        "location": location if location else None,
        "profession": profession if profession else None
    }
    
    return person_info

def research_person(llm, person_info):
    """Research a person using AI - placeholder for now"""
    print(f"\n🔎 Researching: {person_info['name']}")
    print("-" * 40)
    
    # Create search query
    query_parts = [person_info['name']]
    if person_info['company']:
        query_parts.append(person_info['company'])
    if person_info['profession']:
        query_parts.append(person_info['profession'])
    if person_info['location']:
        query_parts.append(person_info['location'])
    
    search_query = " ".join(query_parts)
    print(f"Search Query: {search_query}")
    
    # Placeholder for actual search functionality
    print("\n📋 Research Results:")
    print("=" * 40)
    
    # TODO: Implement actual web search here
    print("🚧 Search functionality coming soon!")
    print(f"Would search for: {search_query}")
    
    return search_query

def main():
    """Main application entry point"""
    print("🚀 Starting Person Research Agent...")
    
    # Load environment variables
    if not load_environment():
        return
    
    # Setup Gemini AI
    llm = setup_gemini()
    if not llm:
        return
    
    print("✅ Environment loaded successfully")
    print("✅ Gemini AI initialized")
    
    while True:
        try:
            # Get person information
            person_info = get_person_info()
            if not person_info:
                continue
            
            # Research the person
            research_person(llm, person_info)
            
            # Ask if user wants to continue
            print("\n" + "=" * 40)
            continue_search = input("Research another person? (y/n): ").strip().lower()
            if continue_search not in ['y', 'yes']:
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            continue

if __name__ == "__main__":
    main() 