# test_checklist.py
# This test verifies that medical condition checkboxes work correctly
# Tests: checking, unchecking, and state verification for each checkbox

# Requirements: pip install pytest pytest-playwright
# Run once: playwright install

from playwright.sync_api import sync_playwright

def test_medical_conditional_check_list():
    """
    Test function that verifies medical condition checklist functionality:
    1. Finds all checkboxes in the medical condition checklist
    2. Tests each checkbox can be checked and unchecked
    3. Verifies the state changes are properly reflected
    """
    
    # Start Playwright browser automation
    with sync_playwright() as p:
        # Launch a Chromium browser (you can see it running)
        browser = p.chromium.launch(headless=False)
        
        # Create a new browser tab/page
        page = browser.new_page()
        
        # Navigate to your local website
        page.goto('http://localhost:3000/')

        # ========================================
        # STEP 1: Find All Checklist Items
        # ========================================
        
        # Example HTML structure we're looking for:
        # <div id="condition-checklist">
        #   <label><input type="checkbox" value="asthma" /> Asthma</label>
        #   <label><input type="checkbox" value="diabetes" /> Diabetes</label>
        #   <label><input type="checkbox" value="vision" /> Vision Problems</label>
        # </div>
        
        # Find all checkbox inputs inside the condition-checklist container
        # This selector means: "Find all input elements with type='checkbox' 
        # that are inside an element with id='condition-checklist'"
        checklist_items = page.query_selector_all("#condition-checklist input[type='checkbox']")
        
        # Verify we found at least one checkbox
        # If no checkboxes found, the test fails with a clear error message
        assert len(checklist_items) > 0, "No items found in the checklist"
        
        print(f"✓ Found {len(checklist_items)} checklist items to test")

        # ========================================
        # STEP 2: Test Each Checkbox Individually
        # ========================================
        
        # Loop through each checkbox and test its functionality
        # enumerate() gives us both the index (i) and the item itself
        for i, item in enumerate(checklist_items):
            # Get the value attribute to identify which condition we're testing
            condition_name = item.get_attribute('value')
            print(f"\n--- Testing Item {i + 1}: {condition_name} ---")
            
            # ========================================
            # STEP 2A: Test Checking the Item
            # ========================================
            
            # Click the checkbox to check it
            # This simulates a user clicking the checkbox
            item.check()
            
            # Verify the checkbox is actually checked
            # is_checked() returns True if checked, False if unchecked
            assert item.is_checked(), f"Item {i + 1} should be checked after check()"
            print(f"✓ Item {i + 1} ({condition_name}) checked successfully")
            
            # Example of what this tests:
            # Before: <input type="checkbox" value="asthma" />  ← unchecked
            # After:  <input type="checkbox" value="asthma" checked />  ← checked
            
            # ========================================
            # STEP 2B: Test Unchecking the Item
            # ========================================
            
            # Click the checkbox again to uncheck it
            # This simulates a user clicking the checkbox again
            item.uncheck()
            
            # Verify the checkbox is actually unchecked
            # not item.is_checked() means "the item should NOT be checked"
            assert not item.is_checked(), f"Item {i + 1} should be unchecked after uncheck()"
            print(f"✓ Item {i + 1} ({condition_name}) unchecked successfully")
            
            # Example of what this tests:
            # Before: <input type="checkbox" value="asthma" checked />  ← checked
            # After:  <input type="checkbox" value="asthma" />  ← unchecked

        # ========================================
        # STEP 3: Test Summary
        # ========================================
        
        print(f"\n All {len(checklist_items)} checklist items tested successfully!")
        print("✓ All checkboxes can be checked")
        print("✓ All checkboxes can be unchecked")
        print("✓ All state changes are properly reflected")
        
        # Test all items checked at once
        print("\n--- Bonus Test: All Items Checked ---")
        for i, item in enumerate(checklist_items):
            item.check()
            condition_name = item.get_attribute('value')
            print(f"  ✓ {condition_name} checked")
        
        print("✓ All items are now checked")
        
        # Test all items unchecked at once
        print("\n--- Bonus Test: All Items Unchecked ---")
        for i, item in enumerate(checklist_items):
            item.uncheck()
            condition_name = item.get_attribute('value')
            print(f"  ✓ {condition_name} unchecked")
        
        print("✓ All items are now unchecked")
        
        # Clean up: Close the browser
        browser.close()

# Run with: python test_checklist.py
if __name__ == "__main__":
    test_medical_conditional_check_list()