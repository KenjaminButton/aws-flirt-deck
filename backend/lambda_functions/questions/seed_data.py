import sys
import os
import boto3
from typing import List, Dict, Any
from datetime import datetime

# Add parent directories to Python path so we can import shared utilities
# Lambda deployment will have these in the same package
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from shared.questions_data import QUESTIONS

# Initialize DynamoDB resource
# boto3 automatically uses AWS credentials from environment
dynamodb = boto3.resource('dynamodb')

# Get table name from environment variable (set by CDK)
# Defaults to 'flirtdeck-table' for local testing
TABLE_NAME = os.environ.get('TABLE_NAME', 'flirtdeck-table')
table = dynamodb.Table(TABLE_NAME)


def transform_question_to_item(question: Dict[str, str]) -> Dict[str, Any]:
    """
    Transform a question dict into DynamoDB item format.
    
    Converts our simple question format into the single-table design pattern.
    
    Args:
        question: Dict with id, text, category keys
        
    Returns:
        DynamoDB item dict with PK, SK, and metadata
        
    Example:
        Input:  {"id": "life_001", "text": "What's your goal?", "category": "life"}
        Output: {"PK": "QUESTION#life_001", "SK": "METADATA", ...}
        
    DynamoDB Structure:
        PK: QUESTION#{question_id}  - Main identifier
        SK: METADATA                - Sort key (allows future expansion)
        GSI1PK: CATEGORY#{category} - For querying by category
        GSI1SK: QUESTION#{id}       - For sorting within category
    """
    timestamp = datetime.utcnow().isoformat()
    
    return {
        # Primary key pattern for single-table design
        'PK': f"QUESTION#{question['id']}",
        'SK': 'METADATA',
        
        # Question data
        'question_id': question['id'],
        'text': question['text'],
        'category': question['category'],
        
        # GSI1 allows querying all questions in a category
        # Example query: "Give me all 'deep' questions"
        'GSI1PK': f"CATEGORY#{question['category']}",
        'GSI1SK': f"QUESTION#{question['id']}",
        
        # Metadata
        'created_at': timestamp,
        'updated_at': timestamp,
        'version': 1  # Track question versions for future updates
    }


def batch_write_items(items: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Write items to DynamoDB in batches for efficiency.
    
    DynamoDB batch_write_item can write up to 25 items at once,
    which is much faster than individual put_item calls.
    
    Args:
        items: List of DynamoDB item dicts to write
        
    Returns:
        Dict with success/failure counts
        
    Example:
        result = batch_write_items(question_items)
        # Returns: {"success": 12, "failed": 0}
    """
    success_count = 0
    failed_count = 0
    
    # Process in batches of 25 (DynamoDB limit)
    batch_size = 25
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        
        try:
            # Prepare batch write request
            # Each item goes into a PutRequest (overwrite if exists)
            with table.batch_writer() as batch_writer:
                for item in batch:
                    batch_writer.put_item(Item=item)
                    success_count += 1
                    
            print(f"✅ Wrote batch {i//batch_size + 1}: {len(batch)} items")
            
        except Exception as e:
            print(f"❌ Error writing batch {i//batch_size + 1}: {str(e)}")
            failed_count += len(batch)
    
    return {
        "success": success_count,
        "failed": failed_count
    }


def seed_questions() -> bool:
    """
    Main function to seed questions into DynamoDB.
    
    Returns:
        True if seeding was successful, False otherwise
    """
    print("\n🌱 Starting questions seed process...")
    print(f"📦 Target table: {TABLE_NAME}")
    print(f"🔢 Questions to seed: {len(QUESTIONS)}")
    
    # Step 1: Check we have questions
    print("\n🔍 Step 1: Checking questions...")
    if not QUESTIONS or len(QUESTIONS) == 0:
        print("❌ No questions found. Aborting seed.")
        return False
    print(f"✅ Found {len(QUESTIONS)} questions")
    
    # Step 2: Transform questions to DynamoDB format
    print("\n🔄 Step 2: Transforming questions to DynamoDB format...")
    items = [transform_question_to_item(q) for q in QUESTIONS]
    print(f"✅ Transformed {len(items)} questions")
    
    # Step 3: Write to DynamoDB
    print("\n📝 Step 3: Writing to DynamoDB...")
    results = batch_write_items(items)
    
    # Step 4: Report results
    print("\n📊 Seed Results:")
    print(f"   ✅ Success: {results['success']} questions")
    print(f"   ❌ Failed:  {results['failed']} questions")
    
    if results['failed'] == 0:
        print("\n🎉 All questions seeded successfully!")
        
        # Print category breakdown
        print("\n📚 Questions by category:")
        categories = {}
        for q in QUESTIONS:
            cat = q['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in sorted(categories.items()):
            print(f"   - {cat}: {count} questions")
        
        return True
    else:
        print(f"\n⚠️  Some questions failed to seed. Check logs above.")
        return False


def handler(event, context):
    """
    Lambda handler for seed script.
    
    This allows running the seed script as a Lambda function
    if needed (e.g., triggered by CloudFormation custom resource).
    
    For now, we'll run it locally with: python seed_data.py
    """
    success = seed_questions()
    
    return {
        "statusCode": 200 if success else 500,
        "body": "Questions seeded successfully" if success else "Seed failed"
    }


if __name__ == "__main__":
    """
    Run seed script directly from command line.
    
    Usage:
        python seed_data.py
        
    Prerequisites:
        - AWS credentials configured (aws configure)
        - TABLE_NAME environment variable set (or uses default)
        - DynamoDB table must exist
    """
    try:
        success = seed_questions()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
