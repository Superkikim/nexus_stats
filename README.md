# 📊 Nexus AI Chat Importer - Statistics Tracker

Automated tracking and analysis of download statistics for the Nexus AI Chat Importer Obsidian plugin.

**[View the plugin →](https://github.com/Superkikim/nexus-ai-chat-importer)**

## 🎯 Current Stats

![Downloads](https://img.shields.io/badge/Total%20Downloads-Loading...-blue)
![Daily Growth](https://img.shields.io/badge/Daily%20Growth-Loading...-green)

> Stats are updated daily at 9:00 AM Paris time via GitHub Actions.

## 📈 Overview

This repository automatically tracks:
- **Total downloads** from Obsidian Community Plugins
- **Version-specific downloads** for each release
- **Daily growth rates** and trends
- **Historical data** (last 90 days)

## 📁 Data Structure

- `daily-stats.json` - Complete daily historical data
- `summary.json` - Current totals and latest changes
- `.github/workflows/stats-collector.yml` - Automation workflow

## 🤖 Automation

- **Frequency**: Daily at 8:00 UTC (9:00 Paris)
- **Source**: [Obsidian Community Plugin Stats](https://github.com/obsidianmd/obsidian-releases/blob/master/community-plugin-stats.json)
- **Notifications**: Telegram bot sends daily updates
- **Storage**: Git history maintains complete tracking

## 📱 Telegram Integration

Automated daily messages include:
- New downloads since last check
- Growth percentage
- Version breakdown
- Total milestone celebrations

## 🔧 Manual Trigger

You can manually trigger stats collection by going to:
**Actions** → **Collect Nexus AI Chat Importer Stats** → **Run workflow**

---

*This tracker helps monitor the adoption and growth of the Nexus AI Chat Importer plugin.*
