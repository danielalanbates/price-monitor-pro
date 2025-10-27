# GitHub Auto-Publishing Setup Guide

## ✅ What's Been Set Up

Your Price Monitor Pro project is now **fully configured for auto-publishing to GitHub**!

### Repository Details
- **GitHub URL**: https://github.com/danielalanbates/price-monitor-pro
- **Branch**: `main`
- **Visibility**: Public
- **License**: MIT

---

## 🤖 Automated Workflows

### 1. **Auto Publish on Push** (`auto-publish.yml`)

**Triggers**: Every push to `main` or `develop`, and all pull requests

**What it does**:
- ✅ Lints Python code with flake8
- ✅ Checks Python formatting with black
- ✅ Lints JavaScript with ESLint
- ✅ Builds Electron app (Linux test build)
- ✅ Updates build status
- 📢 Optional Discord notifications (configure webhook)

**Usage**: Just push code to GitHub!
```bash
git add .
git commit -m "Your changes"
git push
```

The workflow will automatically run tests and build checks.

---

### 2. **Build and Release** (`build-and-release.yml`)

**Triggers**:
- Version tags (e.g., `v1.0.0`, `v2.1.3`)
- Manual trigger via GitHub Actions UI

**What it does**:
- 🍎 Builds macOS DMG installers (Intel + Apple Silicon)
- 🪟 Builds Windows EXE installer
- 🐧 Builds Linux AppImage and .deb packages
- 🧪 Tests Python scripts on all platforms
- 📦 Creates GitHub Release with all installers attached
- 📝 Auto-generates release notes

**Usage**: Create and push a version tag
```bash
# Tag your release
git tag -a v1.0.0 -m "Release v1.0.0 - Initial public release"
git push origin v1.0.0
```

Within ~15-30 minutes, you'll have:
- A new GitHub Release at https://github.com/danielalanbates/price-monitor-pro/releases
- DMG files for macOS (both architectures)
- EXE installer for Windows
- AppImage and .deb for Linux

---

### 3. **CodeQL Security Scan** (`codeql-analysis.yml`)

**Triggers**:
- Every push to `main` or `develop`
- Weekly on Monday at midnight
- All pull requests

**What it does**:
- 🔒 Scans Python and JavaScript code for security vulnerabilities
- 🛡️ Detects common security issues (SQL injection, XSS, etc.)
- 📊 Creates security alerts in GitHub Security tab

**View results**: https://github.com/danielalanbates/price-monitor-pro/security

---

## 📊 GitHub Actions Dashboard

View all workflow runs:
https://github.com/danielalanbates/price-monitor-pro/actions

You'll see:
- ✅ Green checkmarks for passing builds
- ❌ Red X for failing builds
- 🟡 Yellow dot for in-progress builds

---

## 🚀 How to Release a New Version

### Step 1: Update Version Number

Edit `electron-app/package.json`:
```json
{
  "version": "1.0.1",  // Increment this
  ...
}
```

### Step 2: Commit Your Changes
```bash
git add .
git commit -m "Release v1.0.1 - Bug fixes and improvements"
git push
```

### Step 3: Create and Push Tag
```bash
git tag -a v1.0.1 -m "Release v1.0.1

- Fixed price display bug
- Improved eBay scraping
- Updated dependencies
"
git push origin v1.0.1
```

### Step 4: Wait for Build
- GitHub Actions will automatically build for all platforms
- Takes ~15-30 minutes depending on platform
- Check progress: https://github.com/danielalanbates/price-monitor-pro/actions

### Step 5: Publish Release
- Go to: https://github.com/danielalanbates/price-monitor-pro/releases
- Find your new release (will be marked as Draft)
- Edit release notes if needed
- Click "Publish release"

---

## 🎯 Quick Commands Reference

### Everyday Development
```bash
# Make changes to your code
git add .
git commit -m "Description of changes"
git push

# Auto-publish workflow runs automatically ✅
```

### Create New Release
```bash
# Update version in electron-app/package.json first!

git tag -a v1.2.3 -m "Release v1.2.3 - New features"
git push origin v1.2.3

# Build workflow runs automatically and creates release ✅
```

### Manual Workflow Trigger
```bash
# Via GitHub CLI
gh workflow run build-and-release.yml

# Or go to GitHub Actions UI:
# https://github.com/danielalanbates/price-monitor-pro/actions
# Click workflow → "Run workflow" button
```

---

## 🔍 Viewing Build Results

### Build Status Badges
The README now includes badges showing build status:

![Build and Release](https://github.com/danielalanbates/price-monitor-pro/actions/workflows/build-and-release.yml/badge.svg)

### Workflow Logs
- Go to: https://github.com/danielalanbates/price-monitor-pro/actions
- Click on any workflow run
- View detailed logs for each step

### Download Artifacts
- During a build, click "Artifacts" at bottom of workflow page
- Download built installers before release is published

---

## 🛠️ Troubleshooting

### Build Fails on Windows
- Check if `package.json` has correct Windows build config
- Verify electron-builder has Windows signing cert (optional)

### Python Tests Fail
- Check if `requirements.txt` has all dependencies
- Verify Python version compatibility (3.9-3.12 tested)

### DMG Build Fails on macOS
- Ensure icon files exist in `electron-app/assets/`
- Check electron-builder config in `package.json`

### View Detailed Logs
```bash
# Via GitHub CLI
gh run view <run-id> --log

# Or click on failed workflow in GitHub UI
```

---

## 📚 Learned from Similar Projects

Based on research of successful price monitoring projects on GitHub:

### From Crinibus/scraper:
- ✅ SQLite for data storage (we're using JSON, but could upgrade)
- ✅ Product activation/deactivation (TODO: add this feature)
- ✅ Price change detection and cleanup

### From techwithtim/Price-Tracking-Web-Scraper:
- ✅ Playwright for scraping (we use Selenium, both work)
- ✅ Flask/React separation (we use Electron for desktop app)
- ✅ Scheduled automation (we have this!)

### Unique Features in Price Monitor Pro:
- 🎯 Electron desktop app (most projects use web UI)
- 🎯 Multi-platform installers (DMG, EXE, AppImage)
- 🎯 eBay deal finder with auction filtering
- 🎯 No server required (fully local)

---

## 🎨 Optional Enhancements

### Add Discord Notifications
1. Create Discord webhook: Server Settings → Integrations → Webhooks
2. Add webhook URL to GitHub Secrets:
   - Settings → Secrets → New repository secret
   - Name: `DISCORD_WEBHOOK_URL`
   - Value: Your webhook URL
3. Uncomment Discord notification step in `auto-publish.yml`

### Add Code Coverage
```bash
# Install coverage tools
pip install coverage pytest

# Run tests with coverage
coverage run -m pytest
coverage report
```

Add to `auto-publish.yml`:
```yaml
- name: Generate coverage report
  run: coverage run -m pytest && coverage xml

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
```

### Enable Dependabot
Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/electron-app"
    schedule:
      interval: "weekly"

  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## 📖 Next Steps

1. **Test the workflow**: Make a small change and push to see auto-publish in action
2. **Create your first release**: Tag v1.0.0 and watch it build
3. **Monitor builds**: Check the Actions tab regularly
4. **Fix any issues**: Address build failures promptly
5. **Promote your project**: Share the GitHub URL!

---

## 🔗 Important Links

- **Repository**: https://github.com/danielalanbates/price-monitor-pro
- **Actions Dashboard**: https://github.com/danielalanbates/price-monitor-pro/actions
- **Releases**: https://github.com/danielalanbates/price-monitor-pro/releases
- **Security**: https://github.com/danielalanbates/price-monitor-pro/security
- **Issues**: https://github.com/danielalanbates/price-monitor-pro/issues

---

## 🎉 You're All Set!

Your project now has:
- ✅ Automated testing on every commit
- ✅ Multi-platform builds
- ✅ Automatic releases on version tags
- ✅ Security scanning
- ✅ Professional README with badges
- ✅ MIT License

Just code, commit, and push. GitHub Actions handles the rest!

---

**Generated**: October 2025
**Setup by**: Claude Code
**Maintained by**: Daniel Alan Bates
