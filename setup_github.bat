@echo off
echo Setting up GitHub repository for Soko-Mushi...
echo.

REM Initialize git repository
git init

REM Add all files
git add .

REM Create initial commit
git commit -m "Initial commit: Soko-Mushi disk analysis tool"

REM Add remote repository (replace with your actual GitHub repo URL)
echo.
echo Please replace YOUR_USERNAME with your GitHub username in the next command:
echo git remote add origin https://github.com/YOUR_USERNAME/soko-mushi.git
echo.
echo Then run:
echo git branch -M main
echo git push -u origin main
echo.
pause
