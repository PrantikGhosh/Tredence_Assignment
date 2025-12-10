# How to Upload to GitHub

Follow these steps to initialize a git repository and push your code to GitHub.

## 1. Initialize Git
Open your terminal in the project folder (`c:\Users\win11\Desktop\Tredence`) and run:
```bash
git init
```

## 2. Create a .gitignore
Create a file named `.gitignore` to prevent uploading unnecessary files:
```text
__pycache__/
*.pyc
.env
venv/
.vscode/
```
*(You can create this file manually or I can do it for you).*

## 3. Stage and Commit Files
```bash
git add .
git commit -m "Initial commit of Agent Workflow Engine"
```

## 4. Create a Repository on GitHub
1. Go to [github.com/new](https://github.com/new).
2. Enter a repository name (e.g., `agent-workflow-engine`).
3. Click **Create repository**.

## 5. Push to GitHub
Copy the commands shown on GitHub under "…or push an existing repository from the command line" and run them. They will look like this:

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/agent-workflow-engine.git
git push -u origin main
```
