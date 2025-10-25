import discord
from discord.ext import commands
import asyncio
import requests
import random
from datetime import datetime
import os

# Bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

monitored_accounts = {}
META_LOGO = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Meta_Platforms_Inc._logo.svg/1200px-Meta_Platforms_Inc._logo.svg.png"

def check_instagram_status(username):
    """ULTIMATE ACCURATE STATUS DETECTION"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        
        url = f"https://www.instagram.com/{username}/"
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        
        if response.status_code == 404:
            return "restricted"
        elif response.status_code == 200:
            content = response.text.lower()
            if "sorry, this page isn't available" in content:
                return "restricted"
            elif "this account is private" in content:
                return "active"
            elif "log in" in content and "instagram" in content:
                if f"/{username}" not in response.url:
                    return "restricted"
                else:
                    return "active"
            else:
                if f"instagram.com/{username}" in response.url or f"/{username}/" in response.url:
                    return "active"
                else:
                    return "restricted"
        else:
            return "restricted"
    except Exception as e:
        return "active"

@bot.event
async def on_ready():
    print('✅ Meta Instagram Monitor - ONLINE 24/7 on Railway!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Instagram Accounts 24/7"))
    bot.loop.create_task(monitoring_loop())

@bot.event
async def on_message(message):
    if message.author.bot: return
    await bot.process_commands(message)

async def monitoring_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            for username, data in list(monitored_accounts.items()):
                current_status = check_instagram_status(username)
                previous_status = data['status']
                
                if previous_status == "restricted" and current_status == "active":
                    recovery_time = datetime.now() - data['start_time']
                    hours = int(recovery_time.total_seconds() // 3600)
                    minutes = int((recovery_time.total_seconds() % 3600) // 60)
                    
                    embed = discord.Embed(
                        title="✅ **ACCOUNT RESTORED**",
                        color=0x00ff00,
                        timestamp=datetime.now()
                    )
                    embed.set_thumbnail(url=META_LOGO)
                    embed.add_field(
                        name="Account Information",
                        value=f"**Username:** {username}\n**Status:** Active\n**Recovery Time:** {hours}h {minutes}m",
                        inline=False
                    )
                    embed.set_footer(text="Meta Monitoring System • Instant Alert")
                    
                    channel = bot.get_channel(data['channel_id'])
                    if channel:
                        try:
                            await channel.send(embed=embed)
                        except:
                            pass
                    
                    del monitored_accounts[username]
                    continue
                
                if current_status != previous_status:
                    monitored_accounts[username]['status'] = current_status
                    monitored_accounts[username]['last_updated'] = datetime.now()
            
            await asyncio.sleep(60)
        except Exception as e:
            await asyncio.sleep(60)

@bot.command()
async def monitor(ctx, username: str):
    username = ''.join(char for char in username if char.isalnum() or char in '_.').lower().replace('@', '')
    
    if not username:
        return
    
    if username in monitored_accounts:
        embed = discord.Embed(
            title="🔄 **ALREADY MONITORING**",
            description=f"**{username}** is already being monitored.",
            color=0xff9900
        )
        embed.set_thumbnail(url=META_LOGO)
        await ctx.send(embed=embed)
        return
    
    current_status = check_instagram_status(username)
    
    monitored_accounts[username] = {
        'status': current_status,
        'start_time': datetime.now(),
        'channel_id': ctx.channel.id,
        'added_by': ctx.author.name
    }
    
    if current_status == "active":
        embed = discord.Embed(
            title="🟢 **MONITORING STARTED**",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=META_LOGO)
        embed.add_field(
            name="Account Status",
            value=f"**Username:** {username}\n**Status:** Active\n**Platform:** Instagram",
            inline=True
        )
        embed.add_field(
            name="Tracking Info", 
            value=f"**Started:** {datetime.now().strftime('%H:%M')}\n**Added by:** {ctx.author.name}",
            inline=True
        )
    else:
        embed = discord.Embed(
            title="🔴 **RESTRICTION DETECTED**", 
            color=0xff0000,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=META_LOGO)
        embed.add_field(
            name="Account Status",
            value=f"**Username:** {username}\n**Status:** Restricted/Banned\n**Platform:** Instagram", 
            inline=True
        )
        embed.add_field(
            name="Tracking Info",
            value=f"**Started:** {datetime.now().strftime('%H:%M')}\n**Added by:** {ctx.author.name}",
            inline=True
        )
    
    embed.set_footer(text="Meta Platforms Inc. • 24/7 Railway Hosting")
    await ctx.send(embed=embed)

@bot.command()
async def unmonitor(ctx, username: str):
    username = ''.join(char for char in username if char.isalnum() or char in '_.').lower().replace('@', '')
    
    if not username:
        return
        
    if username in monitored_accounts:
        del monitored_accounts[username]
        embed = discord.Embed(
            title="🛑 **MONITORING STOPPED**",
            description=f"Stopped tracking **{username}**",
            color=0xff0000
        )
        embed.set_thumbnail(url=META_LOGO)
        await ctx.send(embed=embed)

@bot.command()
async def list(ctx):
    if not monitored_accounts:
        embed = discord.Embed(
            title="📋 **MONITORING DASHBOARD**",
            description="No accounts being monitored",
            color=0xff9900
        )
        embed.set_thumbnail(url=META_LOGO)
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title="📋 **ACTIVE MONITORING**",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=META_LOGO)
    
    for username, data in monitored_accounts.items():
        status = "🟢 Active" if data['status'] == "active" else "🔴 Restricted"
        monitor_time = datetime.now() - data['start_time']
        hours = int(monitor_time.total_seconds() // 3600)
        
        embed.add_field(
            name=f"@{username}",
            value=f"{status}\n{hours}h watched\nBy: {data['added_by']}",
            inline=True
        )
    
    embed.set_footer(text=f"Meta Systems • Tracking {len(monitored_accounts)} accounts • Railway 24/7")
    await ctx.send(embed=embed)

@bot.command()
async def status(ctx, username: str):
    username = ''.join(char for char in username if char.isalnum() or char in '_.').lower().replace('@', '')
    
    if not username:
        return
        
    current_status = check_instagram_status(username)
    
    if current_status == "active":
        embed = discord.Embed(
            title="🟢 **ACCOUNT ACTIVE**",
            description=f"**{username}** is currently active on Instagram",
            color=0x00ff00
        )
    else:
        embed = discord.Embed(
            title="🔴 **ACCOUNT RESTRICTED**",
            description=f"**{username}** is currently restricted or deactivated",
            color=0xff0000
        )
    
    embed.set_thumbnail(url=META_LOGO)
    embed.set_footer(text="Meta Status Check • Railway Hosting")
    await ctx.send(embed=embed)

@bot.command()
async def test(ctx):
    embed = discord.Embed(
        title="✅ **ACCOUNT RESTORED**",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=META_LOGO)
    embed.add_field(
        name="Account Information",
        value="**Username:** ssxndeep\n**Status:** Active\n**Recovery Time:** 1h 24m",
        inline=False
    )
    embed.set_footer(text="Meta Monitoring System • Railway Test")
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📖 **META MONITORING COMMANDS**",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=META_LOGO)
    
    commands = [
        ("!monitor username", "Start monitoring account"),
        ("!unmonitor username", "Stop monitoring account"), 
        ("!status username", "Check account status"),
        ("!list", "View all monitored accounts"),
        ("!test", "Test recovery alert system")
    ]
    
    for cmd, desc in commands:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text="Meta Platforms Inc. • Railway 24/7 Hosting")
    await ctx.send(embed=embed)

# Use environment variable for token (RAILWAY WILL SET THIS)
bot.run(os.environ.get('DISCORD_BOT_TOKEN'))
