"""
Test Script: Query Questions by Category using GSI1

This script verifies that our questions are properly indexed in DynamoDB
and can be efficiently queried by category.

Purpose:
- Spot check that GSI1 (CATEGORY#{category}) is working
- Verify all 4 categories return questions
- Demonstrate how the GET /questions/random endpoint will work

Think of this like testing a library's card catalog:
- Can we find all "mystery" books? ✓
- Can we find all "romance" books? ✓
- Is the indexing working properly? ✓
"""

import os
import boto3
from typing import List, Dict, Any

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_NAME', 'flirtdeck-table')
table = dynamodb.Table(TABLE_NAME)


def query_questions_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Query all questions in a specific category using GSI1.
    
    This is exactly how our GET /questions/random endpoint will work!
    
    Args:
        category: One of: life, random, deep, experiences
        
    Returns:
        List of question items from DynamoDB
        
    How it works:
        1. Use GSI1 index (much faster than scanning whole table)
        2. Query where GSI1PK = "CATEGORY#{category}"
        3. DynamoDB returns all matching questions instantly
        
    Example:
        questions = query_questions_by_category("life")
        # Returns all 3 "life" questions
    """
    try:
        response = table.query(
            IndexName='GSI1',  # Use our Global Secondary Index
            KeyConditionExpression='GSI1PK = :pk',
            ExpressionAttributeValues={
                ':pk': f'CATEGORY#{category}'
            }
        )
        
        return response.get('Items', [])
    
    except Exception as e:
        print(f"❌ Error querying category '{category}': {str(e)}")
        return []


def test_all_categories():
    """
    Test querying all 4 categories and display results.
    
    This verifies:
    - GSI1 is working correctly
    - All categories have questions
    - Questions are properly structured
    """
    categories = ['life', 'random', 'deep', 'experiences']
    
    print("\n🔍 Testing GSI1 Category Queries")
    print("=" * 60)
    
    total_questions = 0
    
    for category in categories:
        print(f"\n📂 Category: {category.upper()}")
        print("-" * 60)
        
        # Query questions in this category
        questions = query_questions_by_category(category)
        
        if questions:
            print(f"✅ Found {len(questions)} question(s)")
            total_questions += len(questions)
            
            # Display each question
            for i, q in enumerate(questions, 1):
                print(f"\n   {i}. ID: {q['question_id']}")
                print(f"      Text: {q['text']}")
                print(f"      GSI1PK: {q['GSI1PK']}")
                print(f"      GSI1SK: {q['GSI1SK']}")
        else:
            print(f"❌ No questions found (this is a problem!)")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY")
    print("=" * 60)
    print(f"Total questions found: {total_questions}")
    print(f"Expected: 12 (3 per category)")
    
    if total_questions == 12:
        print("\n🎉 SUCCESS! All questions are properly indexed!")
        print("✅ GSI1 is working correctly")
        print("✅ Ready to build GET /questions/random endpoint")
        return True
    else:
        print(f"\n⚠️  WARNING: Expected 12 questions but found {total_questions}")
        print("Check if seed_data.py ran successfully")
        return False


def test_random_selection():
    """
    Bonus test: Simulate how GET /questions/random will work.
    
    This shows how we'll pick a random question from a category.
    """
    import random
    
    print("\n\n🎲 BONUS: Testing Random Question Selection")
    print("=" * 60)
    print("(This is how GET /questions/random will work)\n")
    
    # Pick a random category
    test_category = random.choice(['life', 'random', 'deep', 'experiences'])
    print(f"1️⃣ User requests: GET /questions/random?category={test_category}")
    
    # Query questions in that category
    questions = query_questions_by_category(test_category)
    print(f"2️⃣ Found {len(questions)} questions in '{test_category}' category")
    
    # Pick random question
    if questions:
        random_question = random.choice(questions)
        print(f"3️⃣ Selected random question:")
        print(f"\n   ID: {random_question['question_id']}")
        print(f"   Text: {random_question['text']}")
        print(f"   Category: {random_question['category']}")
        
        print("\n✅ This is exactly what the API will return!")
    else:
        print("❌ No questions available")


if __name__ == "__main__":
    """
    Run the spot check tests.
    
    Usage:
        python test_gsi_query.py
    """
    try:
        print("\n" + "🧪 FLIRTDECK GSI SPOT CHECK".center(60))
        print("Testing that questions can be queried by category\n")
        
        # Test 1: Query all categories
        success = test_all_categories()
        
        # Test 2: Simulate random selection
        if success:
            test_random_selection()
        
        print("\n" + "=" * 60)
        print("✅ Spot check complete!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n💥 Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
