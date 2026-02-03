# Deploy to Render.com - Automated Script

Write-Host "=" -NoNewline; Write-Host "=" * 59
Write-Host "🚀 AI Voice Detection API - Automated Deployment"
Write-Host "=" -NoNewline; Write-Host "=" * 59

# Check if git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git is not installed. Please install Git first."
    exit 1
}

# Initialize git if not already done
if (-not (Test-Path ".git")) {
    Write-Host "`n📦 Initializing Git repository..."
    git init
    git branch -M main
}

# Add all files
Write-Host "`n📝 Adding files to Git..."
git add .

# Commit
Write-Host "`n💾 Committing changes..."
git commit -m "AI Voice Detection API - Production Ready"

# Prompt for GitHub repository URL
Write-Host "`n🔗 GitHub Repository Setup"
Write-Host "Please create a new repository on GitHub and enter the URL below:"
Write-Host "Example: https://github.com/yourusername/ai-voice-detection.git"
$repoUrl = Read-Host "GitHub Repository URL"

if ($repoUrl) {
    Write-Host "`n🌐 Adding remote repository..."
    git remote remove origin 2>$null
    git remote add origin $repoUrl
    
    Write-Host "`n⬆️  Pushing to GitHub..."
    git push -u origin main
    
    Write-Host "`n✅ Code pushed to GitHub successfully!"
    Write-Host ""
    Write-Host "=" -NoNewline; Write-Host "=" * 59
    Write-Host "🎯 NEXT STEPS"
    Write-Host "=" -NoNewline; Write-Host "=" * 59
    Write-Host ""
    Write-Host "1. Go to https://render.com"
    Write-Host "2. Sign up/Login with GitHub"
    Write-Host "3. Click 'New +' → 'Web Service'"
    Write-Host "4. Select your repository: $repoUrl"
    Write-Host "5. Configure:"
    Write-Host "   - Build Command: pip install -r requirements.txt"
    Write-Host "   - Start Command: uvicorn main:app --host 0.0.0.0 --port `$PORT"
    Write-Host "   - Environment Variable:"
    Write-Host "     * Key: API_KEYS"
    Write-Host "     * Value: test-key-123,guvi-api-key-2024"
    Write-Host "6. Click 'Create Web Service'"
    Write-Host "7. Wait 5-10 minutes for deployment"
    Write-Host "8. Your API will be live at: https://YOUR-APP.onrender.com"
    Write-Host ""
    Write-Host "=" -NoNewline; Write-Host "=" * 59
    Write-Host "✅ Ready for deployment!"
    Write-Host "=" -NoNewline; Write-Host "=" * 59
} else {
    Write-Host "`n⚠️  No repository URL provided. Skipping push."
    Write-Host "You can manually push later with:"
    Write-Host "  git remote add origin YOUR_REPO_URL"
    Write-Host "  git push -u origin main"
}

Write-Host "`n📚 For more details, see DEPLOYMENT_RENDER.md"
