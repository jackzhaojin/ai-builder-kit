#!/usr/bin/env node
const fs = require("fs");

const filePath = process.argv[2];
if (!filePath) {
  console.log("Usage: node analyze.js <path-to-excalidraw-file>");
  process.exit(1);
}

const data = fs.readFileSync(filePath, "utf8");
const json = JSON.parse(data);

// Analyze top-level keys
console.log("=== TOP-LEVEL KEYS ===");
Object.keys(json).forEach(k => {
  const val = json[k];
  const size = JSON.stringify(val).length;
  console.log("  " + k + ": " + typeof val + " (" + size + " chars)");
});

// Analyze element types
console.log("\n=== ELEMENT TYPES ===");
const types = {};
json.elements.forEach(el => {
  types[el.type] = (types[el.type] || 0) + 1;
});
Object.entries(types).sort((a,b) => b[1] - a[1]).forEach(([t, c]) => {
  console.log("  " + t + ": " + c);
});

// Analyze a sample element structure
console.log("\n=== SAMPLE RECTANGLE ELEMENT KEYS ===");
const rect = json.elements.find(e => e.type === "rectangle");
if (rect) {
  Object.keys(rect).forEach(k => {
    const val = rect[k];
    const size = JSON.stringify(val).length;
    console.log("  " + k + ": " + JSON.stringify(val).substring(0, 50) + " (" + size + " chars)");
  });
}

// Check for common default values
console.log("\n=== FIELD DISTRIBUTIONS ===");

const fillStyles = {};
const roughness = {};
const opacity = {};
const bgColors = {};
const strokeWidths = {};
const strokeStyles = {};

json.elements.forEach(el => {
  if (el.fillStyle) fillStyles[el.fillStyle] = (fillStyles[el.fillStyle] || 0) + 1;
  if (el.roughness !== undefined) roughness[el.roughness] = (roughness[el.roughness] || 0) + 1;
  if (el.opacity !== undefined) opacity[el.opacity] = (opacity[el.opacity] || 0) + 1;
  if (el.backgroundColor) bgColors[el.backgroundColor] = (bgColors[el.backgroundColor] || 0) + 1;
  if (el.strokeWidth !== undefined) strokeWidths[el.strokeWidth] = (strokeWidths[el.strokeWidth] || 0) + 1;
  if (el.strokeStyle) strokeStyles[el.strokeStyle] = (strokeStyles[el.strokeStyle] || 0) + 1;
});

console.log("fillStyle:", JSON.stringify(fillStyles));
console.log("roughness:", JSON.stringify(roughness));
console.log("opacity:", JSON.stringify(opacity));
console.log("backgroundColor:", JSON.stringify(bgColors));
console.log("strokeWidth:", JSON.stringify(strokeWidths));
console.log("strokeStyle:", JSON.stringify(strokeStyles));

// Check for null/empty values
console.log("\n=== NULL/EMPTY/FALSE COUNTS ===");
let nullCount = 0;
let emptyArrayCount = 0;
let falseCount = 0;
let nullFields = {};
let emptyArrayFields = {};

json.elements.forEach(el => {
  Object.entries(el).forEach(([k, v]) => {
    if (v === null) {
      nullCount++;
      nullFields[k] = (nullFields[k] || 0) + 1;
    }
    if (Array.isArray(v) && v.length === 0) {
      emptyArrayCount++;
      emptyArrayFields[k] = (emptyArrayFields[k] || 0) + 1;
    }
    if (v === false) falseCount++;
  });
});
console.log("null values total: " + nullCount);
console.log("null fields breakdown:", JSON.stringify(nullFields));
console.log("empty arrays total: " + emptyArrayCount);
console.log("empty array fields:", JSON.stringify(emptyArrayFields));
console.log("false booleans: " + falseCount);

// Check appState size
if (json.appState) {
  console.log("\n=== APP STATE ===");
  console.log("appState size: " + JSON.stringify(json.appState).length + " chars");
  console.log("appState keys: " + Object.keys(json.appState).length);
}

// Check files
if (json.files) {
  console.log("\n=== FILES ===");
  console.log("files count: " + Object.keys(json.files).length);
  console.log("files size: " + JSON.stringify(json.files).length + " chars");
}

// Estimate savings
console.log("\n=== SIZE ANALYSIS ===");
const totalSize = data.length;
const elementsSize = JSON.stringify(json.elements).length;
const appStateSize = json.appState ? JSON.stringify(json.appState).length : 0;
const filesSize = json.files ? JSON.stringify(json.files).length : 0;

console.log("Total file size: " + totalSize + " chars (" + (totalSize/1024).toFixed(1) + " KB)");
console.log("Elements: " + elementsSize + " chars (" + ((elementsSize/totalSize)*100).toFixed(1) + "%)");
console.log("AppState: " + appStateSize + " chars (" + ((appStateSize/totalSize)*100).toFixed(1) + "%)");
console.log("Files: " + filesSize + " chars (" + ((filesSize/totalSize)*100).toFixed(1) + "%)");

// Estimate removable fields
console.log("\n=== OPTIMIZATION POTENTIAL ===");
let removableChars = 0;

// Count chars from fields that could be removed
const removableFields = [
  "seed", "versionNonce", "version", "updated"  // These change on every edit, not needed for rendering
];

json.elements.forEach(el => {
  removableFields.forEach(field => {
    if (el[field] !== undefined) {
      // Approximate size: "field":value, = field.length + 3 + value size + 1
      removableChars += field.length + 4 + JSON.stringify(el[field]).length;
    }
  });
});
console.log("Removable metadata fields (seed, version, versionNonce, updated): ~" + removableChars + " chars");

// Null fields
let nullChars = 0;
json.elements.forEach(el => {
  Object.entries(el).forEach(([k, v]) => {
    if (v === null) {
      nullChars += k.length + 7; // "field":null,
    }
  });
});
console.log("Null field entries: ~" + nullChars + " chars");

// Empty arrays
let emptyArrayChars = 0;
json.elements.forEach(el => {
  Object.entries(el).forEach(([k, v]) => {
    if (Array.isArray(v) && v.length === 0) {
      emptyArrayChars += k.length + 5; // "field":[],
    }
  });
});
console.log("Empty array entries: ~" + emptyArrayChars + " chars");

console.log("\nEstimated total removable: ~" + (removableChars + nullChars + emptyArrayChars) + " chars");
console.log("Potential reduction: ~" + (((removableChars + nullChars + emptyArrayChars)/totalSize)*100).toFixed(1) + "%");
