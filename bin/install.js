#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const os = require("os");

const SKILLS_DIR = path.join(os.homedir(), ".pi", "agent", "skills");
const SOURCE_DIR = path.join(__dirname, "..");

const ALL_SKILLS = fs.readdirSync(SOURCE_DIR).filter((name) => {
  const skillPath = path.join(SOURCE_DIR, name, "SKILL.md");
  return fs.existsSync(skillPath);
});

function copyRecursive(src, dest) {
  if (!fs.existsSync(src)) return;
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    for (const child of fs.readdirSync(src)) {
      copyRecursive(path.join(src, child), path.join(dest, child));
    }
  } else {
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
  }
}

function installSkill(name) {
  const src = path.join(SOURCE_DIR, name);
  const dest = path.join(SKILLS_DIR, name);
  if (!fs.existsSync(path.join(src, "SKILL.md"))) {
    console.error(`  ✗ Skill "${name}" not found`);
    return false;
  }
  copyRecursive(src, dest);
  console.log(`  ✓ ${name}`);
  return true;
}

const args = process.argv.slice(2);
const skillsToInstall = args.length > 0 ? args : ALL_SKILLS;

if (args.includes("--list")) {
  console.log("Available skills:");
  ALL_SKILLS.forEach((s) => console.log(`  ${s}`));
  process.exit(0);
}

if (args.includes("--help") || args.includes("-h")) {
  console.log(`Usage: pi-skills [skill-name ...] [--list] [--all]

Install pi-agent skills to ~/.pi/agent/skills/

  pi-skills                  Install all skills
  pi-skills tdd caveman      Install specific skills
  pi-skills --list           List available skills
`);
  process.exit(0);
}

console.log(`Installing ${skillsToInstall.length} skill(s) to ${SKILLS_DIR}...`);
fs.mkdirSync(SKILLS_DIR, { recursive: true });

let installed = 0;
for (const name of skillsToInstall) {
  if (installSkill(name)) installed++;
}
console.log(`\nDone: ${installed}/${skillsToInstall.length} skills installed.`);
