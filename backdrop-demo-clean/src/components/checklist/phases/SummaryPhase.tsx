// ============================================
// PHASE 3: SUMMARY
// ============================================
// todo: reset all the styling to use the ones in global.css
/**
 * Summary Phase: Final view showing all conditions the user selected and their required forms
 * Each condition can be expanded to see its forms
 * Includes a print button to print the entire checklist
 */

import React from "react";
import { Condition } from "../types";

interface SummaryPhaseProps {
    selectedConditionsList: Condition[];
    expandedConditions: Record<string, boolean>;
    toggleConditionSummary: (id: string) => void;
    expandedForms: Record<string, boolean>;
    toggleForm: (id: string, index: number) => void;
    handlePrintChecklist: () => void;
    reset: () => void;
}

const SummaryPhase: React.FC<SummaryPhaseProps> = ({
    selectedConditionsList,
    expandedConditions,
    toggleConditionSummary,
    expandedForms,
    toggleForm,
    handlePrintChecklist,
    reset,
}) => {
    return (
        <div style={{ background: "#f5f5f5", minHeight: "100vh", display: "flex", flexDirection: "column", width: "100%" }}>
            <div style={{ background: "#e5e7eb", padding: "16px 24px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h2 style={{ margin: 0, fontSize: 18, fontWeight: 600 }}>Below are all conditions discussed:</h2>
                <button onClick={reset} style={{ background: "#243e90", color: "#fff", borderRadius: 6, padding: "6px 10px", border: "none" }}>Start Over</button>
            </div>
            <div style={{ flex: 1, padding: "40px 24px", width: "100%", overflowY: "auto" }}>
                <div style={{ maxWidth: "800px", margin: "0 auto", display: "flex", flexDirection: "column", gap: 16 }}>
                    {selectedConditionsList.map((condition) => {
                        const isExpanded = expandedConditions[condition.id];
                        return (
                            <div key={condition.id} style={{ background: "#fff", borderRadius: 8, padding: 24, boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}>
                                <div style={{ display: "flex", justifyContent: "space-between", cursor: "pointer" }} onClick={() => toggleConditionSummary(condition.id)}>
                                    <div style={{ fontSize: 18, fontWeight: 600 }}>Condition: {condition.label}</div>
                                    <span>{isExpanded ? "▲" : "▼"}</span>
                                </div>
                                {isExpanded && (
                                    <div style={{ marginTop: 16 }}>
                                        <div style={{ fontSize: 24, fontWeight: 700, marginBottom: 16, color: "#243e90" }}>Requires Special Circumstance</div>
                                        <p style={{ marginBottom: 24 }}>Based on your replies we think you need a special issuance, please prepare the documents below!</p>
                                        {condition.forms?.map((formName, index) => {
                                            const isFormExpanded = expandedForms[`${condition.id}-${index}`];
                                            return (
                                                <div key={index} style={{ background: "#f5f7fa", padding: 12, borderRadius: 6, marginBottom: 8, cursor: "pointer" }} onClick={() => toggleForm(condition.id, index)}>
                                                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                                                        <span style={{ fontWeight: 500 }}>{formName}</span>
                                                        <span>{isFormExpanded ? "▲" : "▼"}</span>
                                                    </div>
                                                    {isFormExpanded && <div style={{ marginTop: 12, padding: 12, background: "#fff" }}>Form details for {formName}.</div>}
                                                </div>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>
            <div style={{ background: "#4a5568", padding: "16px 24px", display: "flex", justifyContent: "center" }}>
                <button onClick={handlePrintChecklist} style={{ background: "#243e90", color: "#fff", padding: "10px 16px", borderRadius: 6, border: "none" }}>Print Checklist</button>
            </div>
        </div>
    );
};

export default SummaryPhase;