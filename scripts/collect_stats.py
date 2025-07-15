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
            'new_downloads_today': 0,
            'growth_percentage': 0,
            'version_changes': {}
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
    
    def format_telegram_message(self, current_stats, changes, is_significant=True):
        """Format message for Telegram"""
        total_downloads = current_stats.get('downloads', 0)
        
        if not is_significant and changes['new_downloads'] == 0:
            return None
            
        # Header
        message = "📊 *Nexus AI Chat Importer - Daily Stats*\n\n"
        
        # Main stats
        if changes['new_downloads'] > 0:
            message += f"📈 +{changes['new_downloads']} nouveaux téléchargements\n"
            message += f"📱 Total: {total_downloads:,} téléchargements\n"
            
            if changes['growth_percentage'] > 0:
                message += f"🚀 Croissance: +{changes['growth_percentage']:.1f}%\n"
        else:
            message += f"📱 Total: {total_downloads:,} téléchargements\n"
            message += "😴 Pas de nouveaux téléchargements aujourd'hui\n"
        
        # Version breakdown if there are changes
        if changes['version_changes']:
            message += "\n*Versions populaires:*\n"
            for version, change in changes['version_changes'].items():
                total_for_version = current_stats.get(version, 0)
                message += f"• v{version}: +{change} (total: {total_for_version})\n"
        
        # Footer
        message += f"\n📅 {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        
        return message
    
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
        
        # Send Telegram notification
        message = self.format_telegram_message(current_stats, changes)
        if message:
            await self.send_telegram_message(message)
        else:
            print("📱 No significant changes, skipping Telegram notification")

if __name__ == "__main__":
    collector = NexusStatsCollector()
    asyncio.run(collector.run())
