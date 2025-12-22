// ============================================
// PHASE 2: WALKTHROUGH
// ============================================
// todo: reset all the styling to use the ones in global.css
/**
 * Walkthrough Phase: User answers questions for each selected condition
 * Questions appear one at a time, and previous answered questions remain visible
 * When all questions for a condition are answered, shows the results (required forms)
 */

import React from "react";
import { Condition } from "../types";

interface WalkthroughPhaseProps {
    currentCondition: Condition;
    currentQuestionIndex: number;
    setCurrentQuestionIndex: (idx: number) => void;
    answers: Record<string, Record<number, string>>;
    handleAnswer: (conditionId: string, step: number, value: string) => void;
    handlePreviousQuestion: () => void;
    handleNextCondition: () => void;
    isLastCondition: boolean;
    expandedForms: Record<string, boolean>;
    toggleForm: (conditionId: string, index: number) => void;
    hasPreviousQuestion: boolean;
    reset: () => void;
}

const WalkthroughPhase: React.FC<WalkthroughPhaseProps> = ({
    currentCondition,
    currentQuestionIndex,
    setCurrentQuestionIndex,
    answers,
    handleAnswer,
    handlePreviousQuestion,
    handleNextCondition,
    isLastCondition,
    expandedForms,
    toggleForm,
    hasPreviousQuestion,
    reset,
}) => {
    const conditionAnswers = answers[currentCondition.id] || {};
    const currentQuestion = currentCondition.questions[currentQuestionIndex];
    const allQuestionsAnswered = currentCondition.questions.every((q) => conditionAnswers[q.step]);

    // ============================================
    // SUB-PHASE: RESULTS (All Questions Answered)
    // ============================================
    /**
     * If all questions for the current condition are answered, show the results
     * Results display: condition name, "Requires Special Circumstance" message, and required forms
     */
    if (allQuestionsAnswered) {
        return (
            <div className="phase-container">
                <div className="phase-header">
                    <h2 style={{ margin: 0, fontSize: 18 }}>Let's walk through the conditions you selected:</h2>
                    <button onClick={reset} className="btn-primary">Start Over</button>
                </div>
                <div className="phase-content">
                    <div className="content-card">
                        <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>Condition: {currentCondition.label}</div>
                        <div className="status-title">Requires Special Circumstance</div>
                        <p style={{ fontSize: 16, lineHeight: 1.6, marginBottom: 24 }}>Based on your replies we think you need a special issuance, please prepare the documents below on your path to yes!</p>
                        {currentCondition.forms?.map((formName, index) => {
                            const isExpanded = expandedForms[`${currentCondition.id}-${index}`];
                            return (
                                <div key={index} style={{ background: "#f5f7fa", padding: 12, borderRadius: 6, marginBottom: 8, cursor: "pointer" }} onClick={() => toggleForm(currentCondition.id, index)}>
                                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                                        <span style={{ fontWeight: 500 }}>{formName}</span>
                                        <span>{isExpanded ? "▲" : "▼"}</span>
                                    </div>
                                    {isExpanded && <div style={{ marginTop: 12, padding: 12, background: "#fff" }}>Form details for {formName}.</div>}
                                </div>
                            );
                        })}
                    </div>
                </div>
                <div className="phase-footer">
                    <button onClick={() => setCurrentQuestionIndex(currentCondition.questions.length - 1)} style={{ background: "#243e90", color: "#fff", padding: "10px 16px", borderRadius: 6, border: "none" }}>Return to previous Question</button>
                    <button onClick={handleNextCondition} className="btn-primary">{isLastCondition ? "View Summary" : "Next Condition"}</button>
                </div>
            </div>
        );
    }

    // ============================================
    // SUB-PHASE: QUESTIONS (Answering Questions)
    // ============================================
    /**
     * Show all questions in a scrollable view
     * Questions appear as they're answered - once answered, they remain visible
     * Only the current question can be answered (others are disabled)
     */
    const visibleQuestions = currentCondition.questions.filter((q, idx) => conditionAnswers[q.step] || idx === currentQuestionIndex);

    return (
        <div style={{ background: "#f5f5f5", minHeight: "100vh", display: "flex", flexDirection: "column", width: "100%" }}>
            <div style={{ background: "#e5e7eb", padding: "16px 24px", display: "flex", justifyContent: "space-between" }}>
                <h2 style={{ margin: 0, fontSize: 18 }}>Let's walk through the conditions you selected:</h2>
                <button onClick={reset} style={{ background: "#243e90", color: "#fff", borderRadius: 6, padding: "6px 10px", border: "none" }}>Start Over</button>
            </div>
            <div style={{ flex: 1, padding: "40px 24px", width: "100%", overflowY: "auto" }}>
                <div style={{ background: "#fff", borderRadius: 12, padding: "32px", maxWidth: "800px", margin: "0 auto" }}>
                    <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 24 }}>Condition: {currentCondition.label}</div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                        {visibleQuestions.map((q) => {
                            const isCurrent = currentCondition.questions.findIndex(origQ => origQ.step === q.step) === currentQuestionIndex;
                            return (
                                <div key={q.step} style={{ padding: "24px", borderRadius: 8, border: "1px solid #e5e7eb" }}>
                                    <div style={{ fontWeight: 700, marginBottom: 8 }}>Step {q.step}</div>
                                    <div style={{ marginBottom: 20 }}>{q.question}</div>
                                    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                                        {q.options.map((option) => (
                                            <label key={option.value} style={{ display: "flex", gap: 12, cursor: isCurrent ? "pointer" : "default" }}>
                                                <input
                                                    type="radio"
                                                    checked={conditionAnswers[q.step] === option.value}
                                                    disabled={!isCurrent}
                                                    onChange={() => {
                                                        handleAnswer(currentCondition.id, q.step, option.value);
                                                        if (isCurrent && currentQuestionIndex < currentCondition.questions.length - 1) {
                                                            // timeout set for the sake of making sure UI renders correctly
                                                            setTimeout(() => setCurrentQuestionIndex(currentQuestionIndex + 1), 100);
                                                        }
                                                    }}
                                                />
                                                <span>{option.label}</span>
                                            </label>
                                        ))}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
            <div style={{ background: "#4a5568", padding: "16px 24px", display: "flex", justifyContent: "space-between" }}>
                <button onClick={handlePreviousQuestion} disabled={!hasPreviousQuestion} style={{ background: hasPreviousQuestion ? "#243e90" : "#9ca3af", color: "#fff", padding: "10px 16px", borderRadius: 6, border: "none" }}>Return to previous Question</button>
                {!conditionAnswers[currentQuestion.step] && <div style={{ color: "#d1d5db" }}>Please select an answer to continue</div>}
            </div>
        </div>
    );
};

export default WalkthroughPhase;