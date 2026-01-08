import React, { useMemo, useState } from "react";
import BodyMap, { BodyPartKey } from "./BodyMap";

// Sex-specific JSON data
import maleData from "../../data/conditions-male.json";
import femaleData from "../../data/conditions-female.json";
import intersexData from "../../data/conditions-intersex.json";

// Types
type SexAtBirth = "male" | "female" | "intersex" | undefined;
type ConditionsByPart = Record<BodyPartKey, string[]>;

// Button
const Button: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement>> = ({
  children,
  className = "",
  ...props
}) => (
  <button
    {...props}
    className={`px-4 py-2 text-sm font-medium rounded-md bg-[#3b3e85] text-white hover:bg-[#2f326c] ${className}`}
  >
    {children}
  </button>
);

// List view
const ListView: React.FC<{
  data: ConditionsByPart;
  onSelect: (p: BodyPartKey) => void;
}> = ({ data, onSelect }) => {
  const [query, setQuery] = useState("");
  const keys = Object.keys(data) as BodyPartKey[];
  const filtered = keys.filter((k) => k.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="bg-white border border-gray-300 rounded-md p-4 h-full flex flex-col overflow-hidden">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-3 gap-2">
        <h2 className="text-lg font-semibold">List Mode</h2>
        <input
          type="text"
          placeholder="Search body part…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="border border-gray-300 rounded-md px-2 py-1 text-sm w-full sm:w-48"
        />
      </div>

      <div className="overflow-y-auto flex-1 rounded-md border border-gray-200 p-2 bg-gray-50">
        <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {filtered.map((key) => (
            <li
              key={key}
              className="bg-white border border-gray-200 rounded-md p-2 flex flex-col justify-between text-center shadow-sm"
            >
              <span className="text-sm font-medium mb-1">{key}</span>
              <Button className="text-xs py-1 px-2" onClick={() => onSelect(key)}>
                View
              </Button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

// Simple details panel that reads from the selected per-sex dataset
const ConditionsPanel: React.FC<{
  part: BodyPartKey;
  data: ConditionsByPart;
  onReturn: () => void;
}> = ({ part, data, onReturn }) => (
  <div className="flex flex-col bg-white border border-gray-300 rounded-md p-4 h-full">
    <h2 className="text-lg font-semibold mb-2">{part}</h2>
    <p className="text-xs text-gray-600 mb-3">
      Conditions relevant to this body area:
    </p>
    <ul className="list-disc text-sm pl-4">
      {(data[part] ?? []).map((c, i) => (
        <li key={i}>{c}</li>
      ))}
    </ul>
    <div className="mt-auto flex justify-center">
      <Button onClick={onReturn}>Return</Button>
    </div>
  </div>
);

export default function BodyMapFeature() {
  const [mode, setMode] = useState<"map" | "detail" | "List">("map");
  const [selected, setSelected] = useState<BodyPartKey | null>(null);
  const [sex, setSex] = useState<SexAtBirth>(undefined);
  const [age, setAge] = useState<string | undefined>();
  const [workforce, setWorkforce] = useState<string | undefined>();

  // Pick current dataset by sex (default to male if undefined, or show empty)
  const currentData: ConditionsByPart = useMemo(() => {
    if (sex === "female") return femaleData as ConditionsByPart;
    if (sex === "intersex") return intersexData as ConditionsByPart;
    if (sex === "male") return maleData as ConditionsByPart;
    return {} as ConditionsByPart;
  }, [sex]);

  return (
    <div className="bg-gray-100 border border-gray-300 rounded-md p-6 w-full max-w-6xl mx-auto flex flex-col gap-6">
      <h2 className="text-center text-xl md:text-1xl lg:text-2xl font-bold leading-tight">
        What kinds of conditions affect my career?
        </h2>

      <p className="text-center text-sm text-gray-700">
        Use the body map or List list to explore medical conditions relevant to FAA certification.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
        {/* LEFT PANEL */}
        <div className="lg:col-span-2 bg-gray-50 rounded-md border border-gray-300 p-4 flex items-center justify-center">
          {/* Map */}
          {mode === "map" && (
            sex ? (
              <BodyMap
                onPick={(p) => {
                  setSelected(p);
                  setMode("detail");
                }}
              />
            ) : (
              <div className="text-gray-500 italic">Select a sex to view the body map.</div>
            )
          )}

          {/* Detail (per-sex conditions) */}
          {mode === "detail" && selected && (
            <ConditionsPanel
              part={selected}
              data={currentData}
              onReturn={() => setMode("map")}
            />
          )}

          {/* List (per-sex conditions) */}
          {mode === "List" && (
            <ListView
              data={currentData}
              onSelect={(p) => {
                setSelected(p);
                setMode("detail");
              }}
            />
          )}
        </div>

        {/* RIGHT PANEL –> demographics/controls */}
        <div className="flex flex-col gap-4 bg-white border border-gray-300 rounded-md p-4 h-full">
          {/* Sex */}
          <fieldset>
            <legend className="font-semibold text-sm">Sex</legend>
            {(["male", "female", "intersex"] as Array<Exclude<SexAtBirth, undefined>>).map((s) => (
              <label key={s} className="block text-sm">
                <input
                  type="radio"
                  name="sex"
                  className="mr-2"
                  checked={sex === s}
                  onChange={() => {
                    setSex(s);
                    // Return to map on change to reflect correct dataset
                    setMode("map");
                  }}
                />
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </label>
            ))}
          </fieldset>

          {/* Age */}
          <fieldset>
            <legend className="font-semibold text-sm">Age Range</legend>
            {["Below 18", "18-26", "27-36", "37-46", "47-64", "65 and older"].map((opt) => (
              <label key={opt} className="block text-sm">
                <input
                  type="radio"
                  name="age"
                  className="mr-2"
                  checked={age === opt}
                  onChange={() => setAge(opt)}
                />
                {opt}
              </label>
            ))}
          </fieldset>

          {/* Workforce */}
          <fieldset>
            <legend className="font-semibold text-sm">Focused Workforce</legend>
            {[
              "Personal Aircraft Pilot",
              "Commercial Aircraft Pilot",
              "International Aircraft Pilot",
              "Air Traffic Control",
            ].map((opt) => (
              <label key={opt} className="block text-sm">
                <input
                  type="radio"
                  name="workforce"
                  className="mr-2"
                  checked={workforce === opt}
                  onChange={() => setWorkforce(opt)}
                />
                {opt}
              </label>
            ))}
          </fieldset>
        </div>
      </div>

      <div className="flex justify-between items-center">
        <Button
          onClick={() => {
            setSex(undefined);
            setAge(undefined);
            setWorkforce(undefined);
            setSelected(null);
            setMode("map");
          }}
        >
          Reset
        </Button>

        <Button
          onClick={() => setMode(mode === "List" ? "map" : "List")}
        >
          List View
        </Button>
      </div>
    </div>
  );
}
