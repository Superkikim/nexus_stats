# 📊 Nexus AI Chat Importer - Statistics Tracker

Automated tracking and analysis of download statistics for the Nexus AI Chat Importer Obsidian plugin.

**[View the plugin →](https://github.com/Superkikim/nexus-ai-chat-importer)**

## 🎯 Current Stats

![Downloads](https://img.shields.io/badge/Total%20Downloads-6,553-blue)
![Daily Growth](https://img.shields.io/badge/Daily%20Growth-+32-brightgreen)

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

### 🤖 Setting up the Telegram Bot

Before running the automation, you'll need to create a Telegram bot to receive notifications:

1. **Create the bot**: Open Telegram and message `@BotFather`
2. **Start with** `/newbot` and follow the prompts
3. **Choose a name** (e.g., "My Plugin Stats Bot") and **username** (must end with "_bot")
4. **Save the token** BotFather gives you - this goes in GitHub Secrets as `TELEGRAM_BOT_TOKEN`
5. **Get your Chat ID**: Message `@userinfobot` with `/start` to get your personal Chat ID
6. **Test the bot**: Send any message to your new bot to activate the conversation

### 🔐 Adding Secrets to GitHub

To keep your bot credentials secure:

1. **Go to your repository** → **Settings** → **Secrets and variables** → **Actions**
2. **Click "New repository secret"** and add:
   - **Name**: `TELEGRAM_BOT_TOKEN` **Value**: (the token from BotFather)
   - **Name**: `TELEGRAM_CHAT_ID` **Value**: (your Chat ID from userinfobot)
3. **Enable workflow permissions**: Settings → Actions → General → "Read and write permissions"

The automation will send daily reports to this bot, which only you can see. Your token and Chat ID remain private in GitHub Secrets.

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
