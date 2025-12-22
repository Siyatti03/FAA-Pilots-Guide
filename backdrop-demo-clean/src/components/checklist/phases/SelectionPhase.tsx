// ============================================
// PHASE 1: SELECTION
// ============================================
// todo: reset all the styling to use the ones in global.css
/**
 * Selection Phase: User selects which medical conditions apply to them
 * Displays all available conditions with checkboxes
 * Shows sub-conditions when a parent condition (like Mental Health) is selected
 */
import React from "react";
import { Condition } from "../types";
interface SelectionPhaseProps {
    searchTerm: string;
    setSearchTerm: (val: string) => void;
    filteredConditions: Condition[];
    selectedConditions: Record<string, boolean>;
    selectedSubConditions: Record<string, boolean>;
    toggleCondition: (id: string) => void;
    toggleSubCondition: (id: string) => void;
    handleStartWalkthrough: () => void;
    selectedConditionsList: Condition[];
    reset: () => void;
}

const SelectionPhase: React.FC<SelectionPhaseProps> = ({
    searchTerm,
    setSearchTerm,
    filteredConditions,
    selectedConditions,
    selectedSubConditions,
    toggleCondition,
    toggleSubCondition,
    handleStartWalkthrough,
    selectedConditionsList,
    reset,
}) => {
    const hasSelections = selectedConditionsList.length > 0;

    return (
        <div style={{
            padding: "24px",
            background: "#f9fafb",
            minHeight: "100vh",
            display: "flex",
            flexDirection: "column",
            maxWidth: "1000px",
            margin: "0 auto",
        }}>
            {/* Header - Fixed at top */}
            <div style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 20,
                flexShrink: 0,
            }}>
                <h2 style={{ margin: 0, fontSize: 28, fontWeight: 700, color: "#1a1a1a" }}>
                    Select your applicable medical condition(s):
                </h2>
                <button
                    onClick={reset}
                    style={{
                        background: "#243e90",
                        color: "#fff",
                        borderRadius: 6,
                        padding: "8px 16px",
                        border: "none",
                        cursor: "pointer",
                        fontSize: 14,
                        fontWeight: 500,
                    }}
                >
                    Start Over
                </button>
            </div>

            {/* Search Bar */}
            <div style={{ marginBottom: 20, flexShrink: 0 }}>
                <input
                    type="text"
                    placeholder="Search conditions..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    style={{
                        width: "100%",
                        padding: "12px 16px",
                        fontSize: 16,
                        border: "2px solid #e5e7eb",
                        borderRadius: 8,
                        outline: "none",
                        transition: "border-color 0.2s",
                    }}
                />
            </div>

            {/* Selected Count */}
            {hasSelections && (
                <div style={{
                    marginBottom: 16,
                    padding: "12px 16px",
                    background: "#dbeafe",
                    borderRadius: 8,
                    border: "1px solid #93c5fd",
                    flexShrink: 0,
                }}>
                    <span style={{ fontWeight: 600, color: "#1e40af" }}>
                        {selectedConditionsList.length} condition{selectedConditionsList.length !== 1 ? 's' : ''} selected
                    </span>
                </div>
            )}

            {/* Conditions List - Scrollable */}
            <div style={{
                overflowY: "auto",
                overflowX: "hidden",
                flex: 1,
                paddingRight: 8,
                maxHeight: "calc(100vh - 280px)",
            }}>
                <div style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
                    gap: 12,
                }}>
                    {filteredConditions.map((condition) => {
                        const isSelected = selectedConditions[condition.id] || (condition.subConditions && condition.subConditions.some(sc => selectedSubConditions[sc.id]));
                        const showSubConditions = condition.subConditions && (selectedConditions[condition.id] || isSelected);

                        return (
                            <div
                                key={condition.id}
                                style={{
                                    background: "#fff",
                                    padding: 16,
                                    borderRadius: 8,
                                    border: isSelected ? "2px solid #2563EB" : "1px solid #d1d5db",
                                    transition: "all 0.2s",
                                    boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
                                    cursor: "pointer",
                                }}
                                onClick={() => toggleCondition(condition.id)}
                            >
                                <label
                                    style={{ display: "flex", gap: 12, alignItems: "flex-start", cursor: "pointer", marginBottom: showSubConditions ? 12 : 0 }}
                                    onClick={(e) => e.stopPropagation()}
                                >
                                    <input
                                        type="checkbox"
                                        checked={!!selectedConditions[condition.id]}
                                        onChange={() => toggleCondition(condition.id)}
                                        style={{ marginTop: 2, width: 18, height: 18, cursor: "pointer", borderRadius: "50%" }}
                                    />
                                    <div style={{ flex: 1 }}>
                                        <div style={{ fontWeight: 400, fontSize: 16, lineHeight: 1.4, color: "#1a1a1a", marginBottom: 6 }}>
                                            {condition.label}
                                        </div>
                                        <div style={{ color: "#6b7280", fontSize: 13, lineHeight: 1.5 }}>
                                            {condition.desc}
                                        </div>
                                    </div>
                                </label>

                                {showSubConditions && (
                                    <div style={{ marginTop: 12, paddingTop: 12, borderTop: "1px solid #e5e7eb" }}>
                                        <div style={{ fontSize: 12, fontWeight: 600, color: "#6b7280", marginBottom: 8, textTransform: "uppercase" }}>
                                            Sub-conditions:
                                        </div>
                                        {condition.subConditions!.map((subCondition) => (
                                            <div
                                                key={subCondition.id}
                                                style={{ background: "#f9fafb", padding: 10, borderRadius: 6, marginBottom: 6, border: selectedSubConditions[subCondition.id] ? "1px solid #9ca3af" : "1px solid #d1d5db" }}
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    toggleSubCondition(subCondition.id);
                                                }}
                                            >
                                                <label style={{ display: "flex", gap: 10, alignItems: "center", cursor: "pointer" }}>
                                                    <input
                                                        type="checkbox"
                                                        checked={!!selectedSubConditions[subCondition.id]}
                                                        onChange={() => toggleSubCondition(subCondition.id)}
                                                        style={{ width: 16, height: 16 }}
                                                    />
                                                    <div style={{ fontWeight: 400, fontSize: 14, color: "#1a1a1a" }}>
                                                        {subCondition.label}
                                                    </div>
                                                </label>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Bottom Button - Fixed at bottom */}
            <div style={{ marginTop: 24, display: "flex", justifyContent: "flex-end", flexShrink: 0, paddingTop: 20, borderTop: "2px solid #e5e7eb" }}>
                <button
                    onClick={handleStartWalkthrough}
                    disabled={!hasSelections}
                    style={{
                        background: hasSelections ? "#243e90" : "#d1d5db",
                        color: "#fff",
                        padding: "14px 28px",
                        borderRadius: 8,
                        border: "none",
                        cursor: hasSelections ? "pointer" : "not-allowed",
                        fontSize: 16,
                        fontWeight: 600,
                    }}
                >
                    Continue with {selectedConditionsList.length} Selected Condition{selectedConditionsList.length !== 1 ? 's' : ''}
                </button>
            </div>
        </div>
    );
};

export default SelectionPhase;