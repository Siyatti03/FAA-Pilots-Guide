import React from "react";
import bodyOutline from "../../assets/body-outline.png";

export type BodyPartKey =
  | "Head"
  | "Chest"
  | "Abdomen"
  | "Arms"
  | "Hands"
  | "Legs"
  | "Knees"
  | "Feet";

export default function BodyMap({ onPick }: { onPick: (p: BodyPartKey) => void }) {
  // Tuning for zones (px in native 1024x1536 space)
  const TUNE = {
    head:   { cx: 512, cy: 175, r: 95 },
    chest:  { x: 390, y: 420, w: 248, h: 130, rx: 12 },
    abdomen:{ x: 390, y: 560, w: 248, h: 160, rx: 12 },

    armL:   { x: 260, y: 410, w: 100, h: 260, rx: 20 },
    armR:   { x: 664, y: 410, w: 100, h: 260, rx: 20 },

    handL:  { x: 220, y: 790, w: 110, h: 95,  rx: 16 },
    handR:  { x: 694, y: 790, w: 110, h: 95,  rx: 16 },

    // added split legs/knees/feet left & right so can click on either leg/side
    legL:   { x: 390, y: 830, w: 92,  h: 200, rx: 18 },
    legR:   { x: 550, y: 830, w: 92,  h: 200, rx: 18 },

    kneeL:  { x: 380, y: 1100, w: 88,  h: 62,  rx: 16 },
    kneeR:  { x: 550, y: 1100, w: 88,  h: 62,  rx: 16 },

    footL:  { x: 370, y: 1400, w: 95,  h: 80,  rx: 20 },
    footR:  { x: 570, y: 1400, w: 95,  h: 80,  rx: 20 },
  };

  return (
    <div className="flex items-center justify-center h-full">
      <svg
      viewBox="0 0 1024 1536"
      className="h-[460px]"
      xmlns="http://www.w3.org/2000/svg"
      xmlnsXlink="http://www.w3.org/1999/xlink"
      aria-label="Interactive body map"
      preserveAspectRatio="xMidYMid meet"
      >

        {/* Base Body PNG */}
        <image
        href={bodyOutline}
        x="0"
        y="0"
        width="1024"
        height="1536"
        preserveAspectRatio="none"
        style={{ pointerEvents: "none", userSelect: "none" }}
        />



        {/* Head */}
        <circle
          cx={TUNE.head.cx}
          cy={TUNE.head.cy}
          r={TUNE.head.r}
          fill="transparent"
          className="hover:fill-blue-300 cursor-pointer"
          onClick={() => onPick("Head")}
          tabIndex={0}
        >
          <title>Head</title>
        </circle>

        {/* Chest */}
        <rect
          x={TUNE.chest.x}
          y={TUNE.chest.y}
          width={TUNE.chest.w}
          height={TUNE.chest.h}
          rx={TUNE.chest.rx}
          fill="transparent"
          className="hover:fill-blue-300 cursor-pointer"
          onClick={() => onPick("Chest")}
          tabIndex={0}
        >
          <title>Chest</title>
        </rect>

        {/* Abdomen */}
        <rect
          x={TUNE.abdomen.x}
          y={TUNE.abdomen.y}
          width={TUNE.abdomen.w}
          height={TUNE.abdomen.h}
          rx={TUNE.abdomen.rx}
          fill="transparent"
          className="hover:fill-blue-300 cursor-pointer"
          onClick={() => onPick("Abdomen")}
          tabIndex={0}
        >
          <title>Abdomen</title>
        </rect>

        {/* Arms */}
        <rect
          x={TUNE.armL.x}
          y={TUNE.armL.y}
          width={TUNE.armL.w}
          height={TUNE.armL.h}
          rx={TUNE.armL.rx}
          fill="transparent"
          className="hover:fill-blue-300 cursor-pointer"
          onClick={() => onPick("Arms")}
          tabIndex={0}
        >
          <title>Left arm</title>
        </rect>
        <rect
          x={TUNE.armR.x}
          y={TUNE.armR.y}
          width={TUNE.armR.w}
          height={TUNE.armR.h}
          rx={TUNE.armR.rx}
          fill="transparent"
          className="hover:fill-blue-300 cursor-pointer"
          onClick={() => onPick("Arms")}
          tabIndex={0}
        >
          <title>Right arm</title>
        </rect>

        {/* Hands */}
        <rect
          x={TUNE.handL.x}
          y={TUNE.handL.y}
          width={TUNE.handL.w}
          height={TUNE.handL.h}
          rx={TUNE.handL.rx}
          fill="transparent"
          className="hover:fill-blue-300 cursor-pointer"
          onClick={() => onPick("Hands")}
          tabIndex={0}
        >
          <title>Left hand</title>
        </rect>
        <rect
          x={TUNE.handR.x}
          y={TUNE.handR.y}
          width={TUNE.handR.w}
          height={TUNE.handR.h}
          rx={TUNE.handR.rx}
          fill="transparent"
          className="hover:fill-blue-300 cursor-pointer"
          onClick={() => onPick("Hands")}
          tabIndex={0}
        >
          <title>Right hand</title>
        </rect>

        {/* Legs (left anf right both map to "Legs") */}
        <rect
          x={TUNE.legL.x}
          y={TUNE.legL.y}
          width={TUNE.legL.w}
          height={TUNE.legL.h}
          rx={TUNE.legL.rx}
          fill="transparent"
          className="hover:fill-blue-300 cursor-pointer"
          onClick={() => onPick("Legs")}
          tabIndex={0}
        >
          <title>Left leg</title>
        </rect>
        <rect
          x={TUNE.legR.x}
          y={TUNE.legR.y}
          width={TUNE.legR.w}
          height={TUNE.legR.h}
          rx={TUNE.legR.rx}
          fill="transparent"
          className="hover:fill-blue-300 cursor-pointer"
          onClick={() => onPick("Legs")}
          tabIndex={0}
        >
          <title>Right leg</title>
        </rect>

        {/* Knees (left and right both map to "Knees") */}
        <rect
          x={TUNE.kneeL.x}
          y={TUNE.kneeL.y}
          width={TUNE.kneeL.w}
          height={TUNE.kneeL.h}
          rx={TUNE.kneeL.rx}
          fill="transparent"
          className="hover:fill-blue-300 cursor-pointer"
          onClick={() => onPick("Knees")}
          tabIndex={0}
        >
          <title>Left knee</title>
        </rect>
        <rect
          x={TUNE.kneeR.x}
          y={TUNE.kneeR.y}
          width={TUNE.kneeR.w}
          height={TUNE.kneeR.h}
          rx={TUNE.kneeR.rx}
          fill="transparent"
          className="hover:fill-blue-300 cursor-pointer"
          onClick={() => onPick("Knees")}
          tabIndex={0}
        >
          <title>Right knee</title>
        </rect>

        {/* Feet (left and right both map to "Feet") */}
        <rect
          x={TUNE.footL.x}
          y={TUNE.footL.y}
          width={TUNE.footL.w}
          height={TUNE.footL.h}
          rx={TUNE.footL.rx}
          fill="transparent"
          className="hover:fill-blue-300 cursor-pointer"
          onClick={() => onPick("Feet")}
          tabIndex={0}
        >
          <title>Left foot</title>
        </rect>
        <rect
          x={TUNE.footR.x}
          y={TUNE.footR.y}
          width={TUNE.footR.w}
          height={TUNE.footR.h}
          rx={TUNE.footR.rx}
          fill="transparent"
          className="hover:fill-blue-300 cursor-pointer"
          onClick={() => onPick("Feet")}
          tabIndex={0}
        >
          <title>Right foot</title>
        </rect>
      </svg>
    </div>
  );
}
