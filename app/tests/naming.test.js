import assert from "node:assert/strict";
import { buildHrtFilename } from "../src/naming.js";
assert.equal(buildHrtFilename({domain:"PassiveDefense",documentType:"Proposal",projectName:"Eurasia"}), "HRT_PassiveDefense_Proposal_Eurasia.docx");
assert.equal(buildHrtFilename({domain:"PassiveDefense",documentType:"Proposal",projectName:"Eurasia",scope:"Chapter01"}), "HRT_PassiveDefense_Proposal_Eurasia_Chapter01.docx");
assert.equal(buildHrtFilename({domain:"FS",documentType:"Report",projectName:"Project X",revision:"R01"}), "HRT_FS_Report_Project_X_R01.docx");
console.log("naming tests: PASS");
