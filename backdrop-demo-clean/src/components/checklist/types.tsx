// ---- Type Definitions ----
/**
 * Type definition for a medical condition
 * Contains all information needed to display and process a condition
 */
export type Condition = {
  id: string;                    // Unique identifier for the condition
  label: string;                  // Display name shown to users
  desc: string;                  // Description text explaining the condition
  subConditions?: {              // Optional sub-conditions (e.g., Mental Health has GAD, Depression, PTSD)
    id: string;
    label: string;
  }[];
  questions: {                   // Array of questions to ask for this condition
    step: number;                 // Step number (typically starts at 2)
    question: string;             // The question text
    options: {                    // Answer options for the question
      label: string;              // Display text for the option
      value: string;              // Internal value for the option
    }[];
  }[];
  forms?: string[];              // Optional array of form names required for this condition
};

/**
 * Phase type - represents the different stages of the checklist flow
 * - selection: User selects which conditions apply to them
 * - walkthrough: User answers questions for each selected condition
 * - results: Shows results after completing questions for a condition
 * - summary: Final view showing all conditions and their required forms
 */
export type Phase = "selection" | "walkthrough" | "results" | "summary";