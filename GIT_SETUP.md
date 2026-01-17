# Git Setup for doc-gen-agent

## Step 1: Configure Git Locally (This Repo Only)

```bash
cd doc-gen-agent

# Set your second profile's name and email (LOCAL to this repo only)
git config user.name "Your Second Profile Name"
git config user.email "your-second-email@example.com"

# Verify it's set correctly
git config user.name
git config user.email
```

## Step 2: Initialize Git Repository

```bash
# Initialize git repo
git init

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/

# Output files
output/
*.md.bak

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF

# Add all files
git add .

# Make first commit
git commit -m "Initial commit: Step 1.2 - Git change detection"
```

## Step 3: Create GitHub Repository

1. Go to GitHub.com
2. Click "New repository"
3. Name it: `doc-gen-agent`
4. Don't initialize with README (we already have one)
5. Click "Create repository"

## Step 4: Connect and Push

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/doc-gen-agent.git

# Or if using SSH:
# git remote add origin git@github.com:YOUR_USERNAME/doc-gen-agent.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 5: Verify Profile Used

```bash
# Check which profile is configured for this repo
git config user.name
git config user.email

# Check git log to see commits
git log --pretty=format:"%h - %an (%ae) : %s"
```

## Important Notes

- **Local config only**: These settings only apply to `doc-gen-agent` folder
- **Global config unchanged**: Your default profile remains unchanged
- **SSH vs HTTPS**: Use SSH if you have SSH keys set up, otherwise HTTPS
- **Authentication**: GitHub will prompt for credentials on first push

## Troubleshooting

**If you need to change the profile later:**
```bash
cd doc-gen-agent
git config user.name "New Name"
git config user.email "new-email@example.com"
```

**If you need to use a different remote:**
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/doc-gen-agent.git
```
