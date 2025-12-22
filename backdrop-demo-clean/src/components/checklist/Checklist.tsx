/**
 * Author: Dien Mai
 *     Role: Scrum Master 4
 * Purpose: This component creates an interactive medical conditions checklist for pilots.
 *          It guides users through selecting conditions, answering questions, and viewing
 *          required forms and documents. The checklist data is loaded from a JSON file
 *          for easy maintenance.
 */

// ---- Imports ----
import React, { useState, useEffect } from "react";
import { Condition, Phase } from "./types";
import { CONDITIONS } from "./data";
import SelectionPhase from "./phases/SelectionPhase";
import WalkthroughPhase from "./phases/WalkthroughPhase";
import SummaryPhase from "./phases/SummaryPhase";

// ---- Main Component ----
const Checklist: React.FC = () => {
  // ---- State Management ----
  /**
   * State variables that track the user's progress through the checklist
   */
  const [phase, setPhase] = useState<Phase>("selection");                    // Current phase of the checklist
  const [selectedConditions, setSelectedConditions] = useState<Record<string, boolean>>({});  // Main conditions selected by user
  const [selectedSubConditions, setSelectedSubConditions] = useState<Record<string, boolean>>({});  // Sub-conditions selected (e.g., GAD, Depression)
  const [currentConditionIndex, setCurrentConditionIndex] = useState(0);    // Index of the condition currently being processed
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);       // Index of the question currently being answered
  const [answers, setAnswers] = useState<Record<string, Record<number, string>>>({});  // Stores all user answers: {conditionId: {step: answer}}
  const [expandedForms, setExpandedForms] = useState<Record<string, boolean>>({});     // Tracks which forms are expanded in the UI
  const [expandedConditions, setExpandedConditions] = useState<Record<string, boolean>>({});  // Tracks which conditions are expanded in summary view
  const [searchTerm, setSearchTerm] = useState(""); // Search filter state


  // ---- Computed Values ----
  /**
   * Filters the CONDITIONS array to only include conditions that the user has selected.
   * For conditions with sub-conditions (like Mental Health), includes if main condition OR any sub-condition is selected.
   */
  const selectedConditionsList = CONDITIONS.filter((c) => {
    if (c.subConditions) {
      // If condition has sub-conditions, include if main condition is selected OR any sub-condition is selected
      return selectedConditions[c.id] || c.subConditions.some((sc) => selectedSubConditions[sc.id]);
    }
    // Otherwise, check if the main condition is selected
    return selectedConditions[c.id];
  });

  // Get the current condition and question being displayed
  const currentCondition = selectedConditionsList[currentConditionIndex];
  const currentQuestion = currentCondition?.questions[currentQuestionIndex];
  
  // Helper flags to determine navigation state
  const isLastQuestion = currentCondition && currentQuestionIndex === currentCondition.questions.length - 1;
  const isLastCondition = currentConditionIndex === selectedConditionsList.length - 1;
  const hasPreviousQuestion = currentQuestionIndex > 0 || currentConditionIndex > 0;  // Can go back if not on first question/condition

  // ---- Event Handlers ----
  /**
   * Toggles the selection state of a main condition (e.g., Blood Pressure, Mental Health)
   */
  const toggleCondition = (id: string) => {
    setSelectedConditions((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  /**
   * Toggles the selection state of a sub-condition (e.g., GAD, Depression, PTSD under Mental Health)
   */
  const toggleSubCondition = (id: string) => {
    setSelectedSubConditions((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  /**
   * Saves the user's answer to a question
   * @param conditionId - The ID of the condition this question belongs to
   * @param step - The step number of the question
   * @param value - The answer value selected by the user
   */
  const handleAnswer = (conditionId: string, step: number, value: string) => {
    setAnswers((prev) => ({
      ...prev,
      [conditionId]: {
        ...prev[conditionId],
        [step]: value,
      },
    }));
  };

  /**
   * Advances to the next question in the current condition
   * Note: This is mostly handled automatically when an answer is selected
   */
  const handleNextQuestion = () => {
    if (currentCondition && currentQuestionIndex < currentCondition.questions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
    } else {
      // Last question answered - results will show automatically when allQuestionsAnswered is true
      // No need to change state here, the component will re-render and show results
    }
  };

  /**
   * Goes back to the previous question
   * If on the first question of a condition, goes back to the last question of the previous condition
   */
  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      // Go back one question in the current condition
      setCurrentQuestionIndex((prev) => prev - 1);
    } else if (currentConditionIndex > 0) {
      // Go back to previous condition's last question
      const prevCondition = selectedConditionsList[currentConditionIndex - 1];
      setCurrentConditionIndex((prev) => prev - 1);
      setCurrentQuestionIndex(prevCondition.questions.length - 1);
    }
  };

  /**
   * Starts the walkthrough phase after user has selected their conditions
   * Resets to the first condition and first question
   */
  const handleStartWalkthrough = () => {
    if (selectedConditionsList.length > 0) {
      setPhase("walkthrough");
      setCurrentConditionIndex(0);
      setCurrentQuestionIndex(0);
    }
  };

  /**
   * Advances to the next condition after completing all questions for the current condition
   * If it's the last condition, transitions to the summary phase
   */
  const handleNextCondition = () => {
    if (!isLastCondition) {
      // Move to next condition, start at first question
      setCurrentConditionIndex((prev) => prev + 1);
      setCurrentQuestionIndex(0);
    } else {
      // All conditions completed - go to summary
      setPhase("summary");
    }
  };

  /**
   * Toggles the expanded/collapsed state of a form in the results view
   * @param conditionId - The ID of the condition this form belongs to
   * @param formIndex - The index of the form in the condition's forms array
   */
  const toggleForm = (conditionId: string, formIndex: number) => {
    const key = `${conditionId}-${formIndex}`;
    setExpandedForms((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  /**
   * Toggles the expanded/collapsed state of a condition in the summary view
   * @param conditionId - The ID of the condition to toggle
   */
  const toggleConditionSummary = (conditionId: string) => {
    setExpandedConditions((prev) => ({
      ...prev,
      [conditionId]: !prev[conditionId],
    }));
  };

  /**
   * Triggers the browser's print dialog to print the checklist
   * todo: This doesn't work nicely. A future developer will have to address this.
   */
  const handlePrintChecklist = () => {
    window.print();
  };

  /**
   * Resets all state to initial values, returning the user to the selection phase
   */
  const reset = () => {
    setPhase("selection");
    setSelectedConditions({});
    setSelectedSubConditions({});
    setCurrentConditionIndex(0);
    setCurrentQuestionIndex(0);
    setAnswers({});
    setExpandedForms({});
    setExpandedConditions({});
  };

  /**
   * Rendering logic based on phase, going from selection -> walkthrough -> summary
   * Selection is where you select conditions in general, summary is where
   * Walkthrough is where you answer specific questions about specific selections to determine more specific, case-by-case handling (forms, tests, etc.)
   * Summary is where you get the completed list and can print your status. At time of writing, printing is essentially nonfunctional.
   */
  if (phase === "selection") {
    const filteredConditions = CONDITIONS.filter((condition) => {
      if (!searchTerm) return true;
      const searchLower = searchTerm.toLowerCase();
      return (
        condition.label.toLowerCase().includes(searchLower) ||
        condition.desc.toLowerCase().includes(searchLower) ||
        (condition.subConditions?.some(sc => sc.label.toLowerCase().includes(searchLower)))
      );
    });

    return (
      <SelectionPhase
        searchTerm={searchTerm} setSearchTerm={setSearchTerm}
        filteredConditions={filteredConditions} selectedConditions={selectedConditions}
        selectedSubConditions={selectedSubConditions} toggleCondition={toggleCondition}
        toggleSubCondition={toggleSubCondition} handleStartWalkthrough={handleStartWalkthrough}
        selectedConditionsList={selectedConditionsList} reset={reset}
      />
    );
  }

  if (phase === "walkthrough") {
    if (selectedConditionsList.length === 0 || !currentCondition) {
      return <div>No conditions selected. <button onClick={reset}>Back</button></div>;
    }

    return (
      <WalkthroughPhase
        currentCondition={currentCondition} currentQuestionIndex={currentQuestionIndex}
        setCurrentQuestionIndex={setCurrentQuestionIndex} answers={answers}
        handleAnswer={handleAnswer} handlePreviousQuestion={handlePreviousQuestion}
        handleNextCondition={handleNextCondition} isLastCondition={isLastCondition}
        expandedForms={expandedForms} toggleForm={toggleForm}
        hasPreviousQuestion={hasPreviousQuestion} reset={reset}
      />
    );
  }

  if (phase === "summary") {
    return (
      <SummaryPhase
        selectedConditionsList={selectedConditionsList} expandedConditions={expandedConditions}
        toggleConditionSummary={toggleConditionSummary} expandedForms={expandedForms}
        toggleForm={toggleForm} handlePrintChecklist={handlePrintChecklist} reset={reset}
      />
    );
  }

  return null;
};

export default Checklist;