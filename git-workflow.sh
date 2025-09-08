# Git workflow commands for MobileRobot development

# Initial setup
git init
git add .
git commit -m "Initial commit: MobileRobot v1.0.0"

# Add remote origin (replace with your repository URL)
git remote add origin https://github.com/JIaLeChye/MobileRobot.git

# Create and push main branches
git branch -M master
git push -u origin master

# Create develop branch
git checkout -b develop
git push -u origin develop

# Feature development workflow
git checkout develop
git pull origin develop
git checkout -b feature/new-feature
# ... make changes ...
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
# Create pull request to develop

# Release workflow
git checkout develop
git pull origin develop
git checkout -b release/v1.1.0
# ... final testing and version updates ...
git checkout master
git merge release/v1.1.0
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin master
git push origin v1.1.0

# Hotfix workflow
git checkout master
git checkout -b hotfix/v1.0.1
# ... fix critical bug ...
git checkout master
git merge hotfix/v1.0.1
git tag -a v1.0.1 -m "Hotfix v1.0.1"
git checkout develop
git merge master
git push origin master
git push origin develop
git push origin v1.0.1

# Clean up
git branch -d release/v1.1.0
git branch -d hotfix/v1.0.1

# View branches and tags
git branch -a
git tag -l

# Check status and history
git status
git log --oneline --graph --all
