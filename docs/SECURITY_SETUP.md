# Security & Setup Guide

## Important: Protecting Your API Key

Your Hevy API key is **sensitive and should never be committed to GitHub**. Follow these steps to set up safely:

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <your-repo-url> hevy-training-toolkit
   cd hevy-training-toolkit
   ```

2. **Create your local `.env` file**

   ```bash
   cp .env.example .env
   ```

3. **Add your API key to `.env`**

   - Open `.env` in your editor
   - Replace `your_api_key_here` with your actual Hevy API key
   - Get your key from: https://hevy.com/settings?developer

   ```ini
   HEVY_API_KEY=sk_test_xxxxxxxxxxxxx
   ```

4. **Verify `.env` is ignored**

   - The `.env` file is in `.gitignore` and will **never** be committed
   - Only `.env.example` (the template) is in the repository

### Getting Your API Key

1. Go to https://hevy.com/settings?developer
2. Log in with your Hevy account
3. Create or copy your API key
4. Paste it in your local `.env` file

### What Should Never Be Committed

- ❌ `.env` (your actual configuration)
- ❌ Any files with your API key
- ❌ Passwords or personal tokens

### What Is Safe to Commit

- ✅ `.env.example` (template only - no real values)
- ✅ Python source code
- ✅ Documentation
- ✅ Configuration files without secrets

### Verify Before Pushing

Before pushing to GitHub, verify no secrets are exposed:

```bash
# Check what files would be committed
git status

# Verify .env is NOT listed
# Only .env.example should be visible
```

### If You Accidentally Committed Secrets

If you accidentally pushed your API key to GitHub:

1. **Immediately rotate your API key** (at https://hevy.com/settings?developer)
2. Generate a new key to replace the old one
3. Remove the file from Git history (advanced):

   ```bash
   git filter-branch --tree-filter 'rm -f .env' -f HEAD
   git push origin --force-all
   ```

### Additional Security Notes

- Keep your API key confidential - treat it like a password
- Don't share `.env` files with others
- Use unique API keys for different environments (dev, staging, production)
- Rotate keys periodically
- Never hardcode API keys in source files

---

For more information about Git security best practices, see: https://docs.github.com/en/code-security/secret-scanning
