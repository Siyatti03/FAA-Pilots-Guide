# Checklist Data Structure

This directory contains the JSON data file that powers the medical conditions checklist.

## File: `conditions.json`

This file contains all the medical conditions, questions, and forms that appear in the checklist application.

### Structure

The JSON file has the following structure:

```json
{
  "conditions": [
    {
      "id": "unique-id",
      "label": "Display Name",
      "desc": "Description text",
      "subConditions": [
        { "id": "sub-id", "label": "Sub Condition Name" }
      ],
      "questions": [
        {
          "step": 2,
          "question": "Question text?",
          "options": [
            { "label": "Option 1", "value": "value1" },
            { "label": "Option 2", "value": "value2" }
          ]
        }
      ],
      "forms": ["Form Name 1", "Form Name 2"]
    }
  ]
}
```

### Fields

- **id**: Unique identifier for the condition (required)
- **label**: Display name shown to users (required)
- **desc**: Description text explaining the condition (required)
- **subConditions**: Optional array of sub-conditions (e.g., for Mental Health)
- **questions**: Array of questions to ask for this condition (required)
  - **step**: Step number (typically starts at 2)
  - **question**: The question text (required)
  - **options**: Array of answer options (required)
    - **label**: Display text for the option
    - **value**: Internal value for the option
- **forms**: Optional array of form names required for this condition

### Adding a New Condition

1. Add a new object to the `conditions` array
2. Provide a unique `id`
3. Add at least one question
4. Save the file - changes will appear automatically when you refresh the browser

### Modifying Questions

1. Find the condition in the `conditions` array
2. Modify the `questions` array
3. Ensure each question has a `step`, `question`, and `options` array
4. Save the file

### Notes

- The `step` number doesn't need to be sequential, but should be unique within a condition
- Questions are displayed in the order they appear in the `questions` array
- Sub-conditions are optional - only include if the condition has sub-categories
- Forms are optional - only include if the condition requires specific forms

