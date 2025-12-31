#!/bin/bash
# Deploy Setup Script for Jino VPS
# Execute on server: bash DEPLOY_SETUP.sh

echo "========================================"
echo "DEPLOY SETUP SCRIPT"
echo "========================================"

# Step 1: Configure git to use SSH with deploy key
echo ""
echo "Step 1: Configuring git SSH..."
git config --global core.sshCommand "ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no"
git config --global user.email "deploy@hair-purchase.ru"
git config --global user.name "GitHub Actions"
echo "✓ Git configured"

# Step 2: Change remote to SSH
echo ""
echo "Step 2: Changing git remote to SSH..."
cd /opt/hair_purchase_site
git remote set-url origin git@github.com:GiornoGiovanaJoJo/hair_purchase_site.git
echo "✓ Remote updated to: $(git remote get-url origin)"

# Step 3: Test SSH connection
echo ""
echo "Step 3: Testing SSH connection to GitHub..."
ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no git@github.com &>/dev/null
if [ $? -eq 255 ]; then
    echo "⚠ SSH connection test (expected exit code)"
else
    echo "✓ SSH test passed"
fi

# Step 4: Fetch from GitHub
echo ""
echo "Step 4: Testing git fetch..."
git fetch origin main
if [ $? -eq 0 ]; then
    echo "✓ Git fetch successful"
else
    echo "✗ Git fetch failed - check SSH key on GitHub"
    exit 1
fi

# Step 5: Show status
echo ""
echo "========================================"
echo "DEPLOY SETUP COMPLETED"
echo "========================================"
echo ""
echo "Git Configuration:"
git config --global core.sshCommand
echo ""
echo "Git Remote:"
git remote -v
echo ""
echo "SSH Key:"
ls -la ~/.ssh/id_ed25519*
echo ""
echo "Next Steps:"
echo "1. Add this public key to GitHub Deploy Keys:"
echo "   https://github.com/GiornoGiovanaJoJo/hair_purchase_site/settings/keys"
echo ""
echo "2. GitHub Actions will now be able to pull code on deployment"
echo ""
echo "========================================"
