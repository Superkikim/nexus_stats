# scripts/collect_stats.py
import json
import os
import requests
from datetime import datetime
import asyncio
from telegram import Bot

class NexusStatsCollector:
    def __init__(self):
        self.plugin_id = "nexus-ai-chat-importer"
        self.stats_url = "https://github.com/obsidianmd/obsidian-releases/raw/master/community-plugin-stats.json"
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
    def fetch_obsidian_stats(self):
        """Fetch stats from Obsidian releases repo"""
        try:
            response = requests.get(self.stats_url, timeout=30)
            response.raise_for_status()
            all_stats = response.json()
            
            if self.plugin_id not in all_stats:
                raise ValueError(f"Plugin {self.plugin_id} not found in stats")
                
            return all_stats[self.plugin_id]
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return None
    
    def load_existing_data(self):
        """Load existing daily stats and summary"""
        daily_stats = []
        summary = {}
        
        # Load daily stats
        if os.path.exists('daily-stats.json'):
            try:
                with open('daily-stats.json', 'r') as f:
                    daily_stats = json.load(f)
            except Exception as e:
                print(f"Error loading daily stats: {e}")
        
        # Load summary
        if os.path.exists('summary.json'):
            try:
                with open('summary.json', 'r') as f:
                    summary = json.load(f)
            except Exception as e:
                print(f"Error loading summary: {e}")
                
        return daily_stats, summary
    
    def calculate_changes(self, current_stats, previous_summary):
        """Calculate changes since last update"""
        changes = {
            'new_downloads': 0,
            'growth_percentage': 0,
            'version_changes': {},
            'new_versions': []
        }
        
        if not previous_summary:
            return changes
            
        # Calculate total downloads change
        current_total = current_stats.get('downloads', 0)
        previous_total = previous_summary.get('total_downloads', 0)
        changes['new_downloads'] = current_total - previous_total
        
        # Calculate growth percentage
        if previous_total > 0:
            changes['growth_percentage'] = (changes['new_downloads'] / previous_total) * 100
            
        # Calculate version-specific changes
        current_versions = {k: v for k, v in current_stats.items() if k not in ['downloads', 'updated']}
        previous_versions = previous_summary.get('versions', {})
        
        for version, downloads in current_versions.items():
            previous_count = previous_versions.get(version, 0)
            version_change = downloads - previous_count
            
            if version_change > 0:
                changes['version_changes'][version] = version_change
                
            # Check for new versions
            if version not in previous_versions:
                changes['new_versions'].append(version)
                
        return changes
    
    def save_data(self, daily_stats, summary):
        """Save updated data to files"""
        # Save daily stats
        with open('daily-stats.json', 'w') as f:
            json.dump(daily_stats, f, indent=2)
            
        # Save summary
        with open('summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
    
    async def send_telegram_message(self, message):
        """Send message to Telegram"""
        if not self.bot_token or not self.chat_id:
            print("Telegram credentials not configured")
            return False
            
        try:
            bot = Bot(token=self.bot_token)
            await bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            print("Telegram message sent successfully")
            return True
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False
    
    def format_telegram_message(self, current_stats, changes):
        """Format enhanced message for Telegram"""
        total_downloads = current_stats.get('downloads', 0)
        
        # Header with plugin icon
        message = "🔌 *Nexus AI Chat Importer*\n"
        message += "📊 *Daily Download Report*\n\n"
        
        # Main stats section
        message += "📈 *OVERVIEW*\n"
        message += f"📱 {total_downloads:,} total downloads (+{changes['new_downloads']})\n"
        
        if changes['growth_percentage'] > 0:
            message += f"🚀 Growth: +{changes['growth_percentage']:.2f}%\n"
        
        message += "\n"
        
        # Version breakdown - ALL versions sorted by popularity
        current_versions = {k: v for k, v in current_stats.items() 
                          if k not in ['downloads', 'updated']}
        
        if current_versions:
            message += "📋 *VERSION BREAKDOWN*\n"
            
            # Sort versions by download count (descending)
            sorted_versions = sorted(current_versions.items(), 
                                   key=lambda x: x[1], reverse=True)
            
            # Get latest version (highest version number)
            latest_version = max(current_versions.keys(), key=lambda v: tuple(map(int, v.split('.'))))
            
            for version, downloads in sorted_versions:
                # Get change for this version
                change = changes['version_changes'].get(version, 0)
                
                # Format percentage of total
                percentage = (downloads / total_downloads) * 100
                
                # Choose emoji based on version status and activity
                if version == latest_version:
                    emoji = "🌟"  # Latest version
                elif version in changes.get('new_versions', []):
                    emoji = "🆕"  # Brand new version
                elif change > 50:
                    emoji = "🔥"  # Very active
                elif change > 10:
                    emoji = "⚡"  # Active
                elif downloads > 500:
                    emoji = "🏆"  # Popular legacy
                elif downloads > 200:
                    emoji = "💎"  # Stable legacy
                else:
                    emoji = "📜"  # Old version
                
                # Format the line
                change_str = f" (+{change})" if change > 0 else ""
                message += f"{emoji} v{version}: {downloads:,}{change_str} ({percentage:.1f}%)\n"
        
        # Highlight significant changes
        if changes['new_downloads'] > 100:
            message += f"\n🎉 *EXCELLENT!* +{changes['new_downloads']} downloads today!\n"
        elif changes['new_downloads'] > 50:
            message += f"\n🎊 *GREAT!* +{changes['new_downloads']} new downloads!\n"
        elif changes['new_downloads'] > 10:
            message += f"\n👍 +{changes['new_downloads']} new downloads\n"
        elif changes['new_downloads'] == 0:
            message += "\n😴 No new downloads today\n"
        
        # New versions alert
        if changes.get('new_versions'):
            message += f"\n🆕 *NEW VERSION!* v{', v'.join(changes['new_versions'])}\n"
        
        # Milestones celebration
        if total_downloads >= 10000 and (total_downloads - changes['new_downloads']) < 10000:
            message += "\n🏆 *MILESTONE!* 10K downloads reached! 🎉\n"
        elif total_downloads >= 5000 and (total_downloads - changes['new_downloads']) < 5000:
            message += "\n🏆 *MILESTONE!* 5K downloads reached! 🎉\n"
        elif total_downloads >= 3000 and (total_downloads - changes['new_downloads']) < 3000:
            message += "\n🏆 *MILESTONE!* 3K downloads reached! 🎉\n"
        
        # Footer with timestamp in Swiss format and CET timezone
        from datetime import timezone, timedelta
        
        # Convert to CET (UTC+1) or CEST (UTC+2 during summer time)
        now_utc = datetime.now(timezone.utc)
        
        # Simple CET/CEST calculation (CET is UTC+1, CEST is UTC+2 from late March to late October)
        # This is a simplified version - for production you'd use pytz
        month = now_utc.month
        day = now_utc.day
        
        # Approximate DST: last Sunday in March to last Sunday in October
        is_dst = month > 3 and month < 10 or (month == 3 and day >= 25) or (month == 10 and day < 25)
        offset_hours = 2 if is_dst else 1
        
        cet_time = now_utc + timedelta(hours=offset_hours)
        timezone_name = "CEST" if is_dst else "CET"
        
        message += f"\n📅 {cet_time.strftime('%d.%m.%Y %H:%M')} {timezone_name}"
        
        return message
        
    def update_readme_badges(self, current_stats, changes):
        """Update README.md with current stats badges"""
        total_downloads = current_stats.get('downloads', 0)
        daily_change = changes.get('new_downloads', 0)
        
        # Read current README
        readme_content = ""
        if os.path.exists('README.md'):
            with open('README.md', 'r', encoding='utf-8') as f:
                readme_content = f.read()
        
        # Update badges with current data
        # Total Downloads badge
        total_badge = f"![Downloads](https://img.shields.io/badge/Total%20Downloads-{total_downloads:,}-blue)"
        readme_content = self.replace_badge_line(readme_content, "Total%20Downloads", total_badge)
        
        # Daily Growth badge
        if daily_change > 0:
            growth_badge = f"![Daily Growth](https://img.shields.io/badge/Daily%20Growth-+{daily_change}-brightgreen)"
        elif daily_change == 0:
            growth_badge = f"![Daily Growth](https://img.shields.io/badge/Daily%20Growth-0-yellow)"
        else:
            growth_badge = f"![Daily Growth](https://img.shields.io/badge/Daily%20Growth-{daily_change}-red)"
            
        readme_content = self.replace_badge_line(readme_content, "Daily%20Growth", growth_badge)
        
        # Write updated README
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
            
        print("📖 README badges updated successfully")
    
    def replace_badge_line(self, content, badge_type, new_badge):
        """Replace a specific badge line in README content"""
        import re
        
        # Pattern to match the badge line
        pattern = rf'!\[[^\]]*\]\(https://img\.shields\.io/badge/{badge_type}[^)]*\)'
        
        if re.search(pattern, content):
            # Replace existing badge
            return re.sub(pattern, new_badge, content)
        else:
            # If badge not found, return content unchanged
            print(f"Warning: Could not find {badge_type} badge to update")
            return content
    
    async def run(self):
        """Main execution function"""
        print("🔄 Starting stats collection...")
        
        # Fetch current stats
        current_stats = self.fetch_obsidian_stats()
        if not current_stats:
            print("❌ Failed to fetch stats")
            return
            
        print(f"✅ Fetched stats: {current_stats['downloads']} total downloads")
        
        # Load existing data
        daily_stats, previous_summary = self.load_existing_data()
        
        # Calculate changes
        changes = self.calculate_changes(current_stats, previous_summary)
        
        # Create new daily entry
        today_entry = {
            'date': datetime.now().isoformat(),
            'stats': current_stats,
            'changes': changes
        }
        
        # Update daily stats (keep last 90 days)
        daily_stats.append(today_entry)
        daily_stats = daily_stats[-90:]  # Keep only last 90 days
        
        # Update summary
        new_summary = {
            'last_updated': datetime.now().isoformat(),
            'total_downloads': current_stats.get('downloads', 0),
            'versions': {k: v for k, v in current_stats.items() if k not in ['downloads', 'updated']},
            'daily_change': changes['new_downloads'],
            'growth_percentage': changes['growth_percentage']
        }
        
        # Save data
        self.save_data(daily_stats, new_summary)
        print("💾 Data saved successfully")
        
        # Update README badges
        self.update_readme_badges(current_stats, changes)
        
        # Send Telegram notification (always send, even if no changes)
        message = self.format_telegram_message(current_stats, changes)
        await self.send_telegram_message(message)

if __name__ == "__main__":
    collector = NexusStatsCollector()
    asyncio.run(collector.run())