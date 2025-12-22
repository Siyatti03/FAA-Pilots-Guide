// This file exists for loading condition data for the checklist.

import conditionsData from "../../data/conditions.json";
import { Condition } from "./types";

export const CONDITIONS: Condition[] =
    (conditionsData as { conditions: Condition[] }).conditions;
