# Command Reference

All git and bash commands used in this project.

---

## Initial Project Setup

### Create Project Structure
```bash
cd ~
./create-project-home.sh
```

### Navigate to Project
```bash
cd ~/health-enrollment-assistant-dev
```

---

## Git Repository Setup

### Create GitHub Repository
```bash
gh repo create health-enrollment-assistant-dev --public --description "Health insurance enrollment assistant with RAG/Agent system"
```

### Initialize Git
```bash
git init
```

### Stage All Files
```bash
git add .
```

### Initial Commit
```bash
git commit -m "Initial project structure

- Created folder structure (docs, data, src, notebooks, tests)
- Added documentation directories (architecture, faqs, readings, notes, decisions)
- Set up basic README files"
```

### Set Main Branch
```bash
git branch -M main
```

### Add Remote Origin
```bash
git remote add origin https://github.com/sudhirshivaram/health-enrollment-assistant-dev.git
```

### Push to GitHub
```bash
git push -u origin main
```

---

## Tracking Empty Folders

### Add .gitkeep Files
```bash
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch src/.gitkeep
touch notebooks/.gitkeep
touch tests/.gitkeep

git add .
git commit -m "Add empty folder structure with .gitkeep files"
git push
```

---

## Git Common Commands

### Check Status
```bash
git status
```

### Check Current Branch
```bash
git branch
```

### Check Remote URL
```bash
git remote -v
```

### Check Commit History
```bash
git log
git log --oneline
```

### Rename Branch
```bash
git branch -M <new-name>
```

---

## Feature Branch Workflow

### Create New Feature Branch
```bash
git checkout -b phase-1-simple-rag
```

### Switch Between Branches
```bash
git checkout main
git checkout phase-1-simple-rag
```

### Push Feature Branch
```bash
git push -u origin phase-1-simple-rag
```

### Merge Feature Branch to Main
```bash
git checkout main
git merge phase-1-simple-rag
git push
```

---

## File Management

### Copy Files
```bash
cp source-file destination-file
```

### Remove Files/Directories
```bash
rm filename
rm -rf directory-name
```

### List Files
```bash
ls
ls -la
```

### Create Directory
```bash
mkdir directory-name
mkdir -p parent/child/grandchild
```

### Create Empty File
```bash
touch filename
```

---

## Navigation

### Change Directory
```bash
cd directory-name
cd ~                  # Home directory
cd ..                 # Parent directory
cd -                  # Previous directory
```

### Print Working Directory
```bash
pwd
```

---

## Project-Specific Scripts

### Create Project Structure
```bash
cd ~/energy-consumption-dev/project-ideas
./create-project-home.sh
```

### Copy Documentation
```bash
cp /home/bhargav/energy-consumption-dev/project-ideas/insurance-rag-system.md ~/health-enrollment-assistant-dev/docs/notes/
cp /home/bhargav/energy-consumption-dev/project-ideas/health-enrollment-discussions.md ~/health-enrollment-assistant-dev/docs/notes/
```

---

## Planned Branching Strategy

```
main (stable, production-ready)
├── phase-1-simple-rag         # Basic RAG implementation
├── phase-2-smart-routing      # Add query classification and routing
├── phase-3-light-agents       # Light agent orchestration
└── phase-4-full-agentic       # Full agentic system
```

### When Starting Each Phase
```bash
git checkout main
git pull
git checkout -b phase-X-description
# Do your work
git add .
git commit -m "Descriptive message"
git push -u origin phase-X-description
# Create PR on GitHub when ready
```

---

## More commands will be added as we progress...
