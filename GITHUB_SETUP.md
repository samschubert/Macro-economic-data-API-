# 🚀 GitHub Pages Setup Guide

Your macro data API is ready to publish! Follow these steps to make it publicly accessible.

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `macro-data-api` (or any name you prefer)
3. **Make it PUBLIC** (required for GitHub Pages)
4. **DO NOT** initialize with README (we already have one)
5. Click "Create repository"

## Step 2: Push Your Code

GitHub will show you commands. Use these:

```bash
cd /Users/samschubert

# Add the remote (replace YOUR-USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR-USERNAME/macro-data-api.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Click **Pages** (left sidebar)
4. Under "Source", select: **Deploy from a branch**
5. Under "Branch", select: **main** and **/ (root)**
6. Click **Save**

Wait 1-2 minutes for deployment.

## Step 4: Access Your API

Your data will be available at:

```
https://YOUR-USERNAME.github.io/macro-data-api/macro_data_api.json
https://YOUR-USERNAME.github.io/macro-data-api/macro_dashboard.html
https://YOUR-USERNAME.github.io/macro-data-api/macro_data_api.html
```

## Step 5: Use with Claude

Now any Claude instance can access your data!

### Example Prompt:

```
Fetch the macro data from https://YOUR-USERNAME.github.io/macro-data-api/macro_data_api.json
and analyze the copper/gold ratio thesis. Focus on the 0.845 correlation with
manufacturing and the Bitcoin cycle timing patterns.
```

### For Article Writing:

```
I've uploaded 5 thesis charts. Also fetch my live data API from
https://YOUR-USERNAME.github.io/macro-data-api/macro_data_api.json

Write a Twitter thread about the copper/gold ratio at 50-year lows as a major
risk-on signal. Use the specific statistics from the API (0.845 correlation,
current ratio of 0.001262, etc.) and reference the charts.
```

## 🔄 Updating Your Data

When you want to refresh the data:

```bash
cd /Users/samschubert

# Update the database
python3 macro_database.py

# Regenerate API export
python3 export_data_api.py

# Regenerate charts (optional)
python3 regenerate_all_charts.py

# Commit and push updates
git add macro_data_api.json macro_data_api.html *.png
git commit -m "Update data: $(date +%Y-%m-%d)"
git push

# Wait 1-2 minutes for GitHub Pages to rebuild
```

## 📊 What's Included

Your repository now contains:
- ✅ 39 economic indicators in JSON format
- ✅ 13 chart images (PNG)
- ✅ Interactive HTML dashboard
- ✅ API documentation page
- ✅ Reference documents for article writing
- ✅ Complete README with usage instructions

## 🔗 Quick Links (After Setup)

Replace `YOUR-USERNAME` with your GitHub username:

- **Main API**: `https://YOUR-USERNAME.github.io/macro-data-api/macro_data_api.json`
- **Dashboard**: `https://YOUR-USERNAME.github.io/macro-data-api/macro_dashboard.html`
- **Chart 1 (6-month lead)**: `https://YOUR-USERNAME.github.io/macro-data-api/thesis_chart1_copper_gold_leads_ism.png`
- **Chart 2 (S&P 500)**: `https://YOUR-USERNAME.github.io/macro-data-api/thesis_chart2_copper_gold_vs_sp500.png`
- **Chart 3 (Bitcoin)**: `https://YOUR-USERNAME.github.io/macro-data-api/thesis_chart3_copper_gold_vs_bitcoin.png`
- **Chart 4 (Liquidity)**: `https://YOUR-USERNAME.github.io/macro-data-api/thesis_chart4_liquidity_dashboard.png`
- **Chart 5 (Dollar)**: `https://YOUR-USERNAME.github.io/macro-data-api/thesis_chart5_copper_gold_vs_dollar.png`

## 💡 Pro Tips

1. **Bookmark your API URL** for easy reference
2. **Update weekly** to keep data fresh (run the update commands above)
3. **Share the dashboard URL** - it's a great visual reference
4. **Use with Claude Code** - just reference the JSON URL in your prompts
5. **Check the `last_updated` field** in the JSON to see data freshness

## 🆘 Troubleshooting

**"404 Not Found" after enabling Pages?**
- Wait 2-3 minutes for initial deployment
- Check Settings > Pages shows "Your site is live at..."
- Make sure repository is PUBLIC

**Charts not loading in dashboard?**
- Charts load from same directory as HTML file
- All PNG files are included in the repo
- Check browser console for errors

**Want to use a custom domain?**
- Go to Settings > Pages > Custom domain
- Add your domain (e.g., macro-data.com)
- Update DNS settings at your registrar

## ✅ Verification

After setup, test these URLs (replace YOUR-USERNAME):

1. `https://YOUR-USERNAME.github.io/macro-data-api/` - Should show README
2. `https://YOUR-USERNAME.github.io/macro-data-api/macro_data_api.json` - Should show JSON data
3. `https://YOUR-USERNAME.github.io/macro-data-api/macro_dashboard.html` - Should show dashboard

If all three work, you're live! 🎉

---

**Need Help?**

If you get stuck:
1. Check the GitHub Pages documentation: https://pages.github.com/
2. Ensure repository is PUBLIC
3. Verify branch is set to "main" in Pages settings
4. Wait a few minutes after enabling Pages

**Ready to go?** Start with Step 1 above! 🚀
