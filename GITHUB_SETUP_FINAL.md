# 🚀 GitHub Deployment Setup - FINAL

## ✅ Server Configuration: DONE

```
DEPLOYHOST:  195.161.69.221
DEPLOYUSER:  root
DEPLOYPORT:  22
PUBLIC_KEY:  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMf/Do93FPXvKE+yZfMNV9vXmNCkBsYor5WxTeM6vFfG
PRIVATE_KEY: (stored securely)
```

---

## 🔐 Step 1: Add Deploy Key to GitHub (MUST DO)

**⚠️ IMPORTANT: This step is REQUIRED for deployment to work**

### Action:
1. Go to: https://github.com/GiornoGiovanaJoJo/hair_purchase_site/settings/keys
2. Click **"Add deploy key"**
3. Fill in:
   - **Title:** `Jino VPS Deploy Key`
   - **Key:** Copy-paste this entire line:
   ```
   ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMf/Do93FPXvKE+yZfMNV9vXmNCkBsYor5WxTeM6vFfG github-deploy
   ```
   - **✅ Allow write access:** CHECK THIS BOX
4. Click **"Add key"**

**Status: ⏳ WAITING FOR MANUAL GITHUB ACTION**

---

## 🔑 Step 2: Set GitHub Secrets (Auto-configured)

**Location:** https://github.com/GiornoGiovanaJoJo/hair_purchase_site/settings/secrets/actions

### Required Secrets:

| Secret Name | Value | Status |
|-------------|-------|--------|
| `DEPLOYHOST` | `195.161.69.221` | ✅ Ready |
| `DEPLOYUSER` | `root` | ✅ Ready |
| `DEPLOYPORT` | `22` | ✅ Ready |
| `DEPLOYSSHKEY` | (private key) | ⏳ Manual add |

### Private Key Content:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACDH/w6PdxT17yhPsmXzDVfb15jQpAbGKK+VsU3jOrxXxgAAAJBajIiyWoyI
sgAAAAtzc2gtZWQyNTUxOQAAACDH/w6PdxT17yhPsmXzDVfb15jQpAbGKK+VsU3jOrxXxg
AAAEBuUPvN/DEXuQzWVQ1IKFLv37RWOZaFiBhkEWYgX/Wn+8f/Do93FPXvKE+yZfMNV9vX
mNCkBsYor5WxTeM6vFfGAAAADWdpdGh1Yi1kZXBsb3k=
-----END OPENSSH PRIVATE KEY-----
```

### How to Add Private Key Secret:
1. Go to: https://github.com/GiornoGiovanaJoJo/hair_purchase_site/settings/secrets/actions
2. Click **"New repository secret"**
3. **Name:** `DEPLOYSSHKEY`
4. **Value:** (paste entire private key from above, including BEGIN and END lines)
5. Click **"Add secret"**

---

## ✅ Server Configuration Already Done

On server `/opt/hair_purchase_site`:
```bash
✅ Git remote: git@github.com:GiornoGiovanaJoJo/hair_purchase_site.git
✅ SSH config: ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no
✅ Git user: deploy@hair-purchase.ru
```

**Error "Permission denied (publickey)" is NORMAL** - it will be fixed after Deploy Key is added.

---

## 🚀 After Setup Complete

Once Deploy Key is added and secrets are configured:

```bash
# On server, test:
git fetch origin main

# Should work without errors
```

Then push to main:
```bash
git push origin main
```

GitHub Actions will:
1. ✅ Run tests
2. ✅ Connect to Jino via SSH
3. ✅ Pull latest code
4. ✅ Run migrations
5. ✅ Restart services

---

## 📋 Checklist

- [ ] Deploy Key added to GitHub
- [ ] DEPLOYSSHKEY secret added
- [ ] DEPLOYHOST secret added  
- [ ] DEPLOYUSER secret added
- [ ] DEPLOYPORT secret added
- [ ] `git fetch origin main` works on server
- [ ] Push to main triggers GitHub Actions

---

**Status: ⏳ AWAITING MANUAL GITHUB SETUP**
