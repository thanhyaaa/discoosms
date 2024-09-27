import discord
from discord.ext import commands
import datetime
import sqlite3
import subprocess
import os
import asyncio
import random
import collections
from discord import Embed

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

TOKEN = os.getenv('DISCORD_TOKEN')

# Constants
ALLOWED_CHANNEL_ID = 1264975987934761121
ALLOWED_GUILD_ID = 1264973683877744798
TEMP_ROLE_ID = 1264997863079940170
ROLE_ID = 1264975463672057907
SPECIAL_ROLE_ID = 1265025672225493223
LOG_CHANNEL_ID = 1266421667849043978
INVALID_NUMBERS = ['113', '911', '114', '115', '84357156328', '0357156328']
VIP_CHANNEL_ID = 1268130522731905079
VIP_ROLE_ID = 1268131048575729665

# Database setup
try:
    connection = sqlite3.connect('user_data.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            expiration_time TEXT
        )
    ''')
    connection.commit()
except sqlite3.Error as e:
    print(f"Lỗi kết nối cơ sở dữ liệu: {e}")

# State storage
processes = {}
recent_gifs = collections.deque(maxlen=4)
GIF_URLS = [
    "https://c.tenor.com/LmJ_S8wzHlkAAAAd/tenor.gif",
    "https://c.tenor.com/_zPDmll9gtYAAAAC/tenor.gif",
    "https://c.tenor.com/5eOY_XtahDoAAAAC/tenor.gif",
    "https://c.tenor.com/btBDlEIT5xUAAAAd/tenor.gif",
    "https://c.tenor.com/I-vY-Iq3zggAAAAC/tenor.gif",
    "https://c.tenor.com/zb0UToCgW9gAAAAC/tenor.gif",
    "https://c.tenor.com/XJS7LmGwm5QAAAAC/tenor.gif",
    "https://c.tenor.com/EqJh0gyBX5wAAAAd/tenor.gif",
    "https://c.tenor.com/wkz3IcpxCEUAAAAd/tenor.gif",
    "https://c.tenor.com/s73hsxgU3IAAAAAd/tenor.gif",
    "https://c.tenor.com/7plyfBPAR3AAAAAd/tenor.gif",
    "https://c.tenor.com/ejdvSGj5kCYAAAAC/tenor.gif",
    "https://c.tenor.com/xD5CN6oj8ysAAAAC/tenor.gif",
    "https://c.tenor.com/6Myx4MF6DjIAAAAC/tenor.gif",
    "https://c.tenor.com/2BmAiarixGAAAAAC/tenor.gif",
    "https://c.tenor.com/i5r1lXIAJgEAAAAd/tenor.gif",
    "https://c.tenor.com/1nwkeOg8j48AAAAd/tenor.gif",
    "https://c.tenor.com/5wn9MtW_PYUAAAAd/tenor.gif",
    "https://c.tenor.com/L6bKFEaUkp0AAAAC/tenor.gif",
    "https://c.tenor.com/q3hjT73igbwAAAAC/tenor.gif",
    "https://c.tenor.com/QjMLx8tgJ0UAAAAC/tenor.gif",
    "https://c.tenor.com/4a8oLL-3PYAAAAAd/tenor.gif",
    "https://c.tenor.com/rycw44X648oAAAAd/tenor.gif",
    "https://c.tenor.com/M3BzTbU81uIAAAAd/tenor.gif",
    "https://c.tenor.com/fi1SSaUNyC8AAAAC/tenor.gif",
    "https://c.tenor.com/lcJxNSzW8MUAAAAC/tenor.gif",
    "https://c.tenor.com/PwA7hjm2oVIAAAAd/tenor.gif",
    "https://c.tenor.com/quduIlTKjWwAAAAd/tenor.gif",
    "https://c.tenor.com/9djzdAaY9Z8AAAAd/tenor.gif",
    "https://c.tenor.com/G4OcrlG79AYAAAAC/tenor.gif",
    "https://c.tenor.com/3kuJ1ZABvCoAAAAd/tenor.gif",
    "https://c.tenor.com/tu-cBstJDtEAAAAd/tenor.gif",
    "https://c.tenor.com/yVlyIA6v-_YAAAAC/tenor.gif",
    "https://c.tenor.com/L6gAWJ03Cz0AAAAd/tenor.gif"
]

def TimeStamp():
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime('%Y-%m-%d %I:%M:%S %p')

def get_random_gif_url():
    available_gifs = [url for url in GIF_URLS if url not in recent_gifs]
    if not available_gifs:
        available_gifs = GIF_URLS
        recent_gifs.clear()
    chosen_gif = random.choice(available_gifs)
    recent_gifs.append(chosen_gif)
    return chosen_gif

async def log_to_channel(username, user_id, phone_number, count, execution_time):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        log_message = f"{username} ||{user_id}|| {phone_number} x**{count}** - {execution_time}\n"
        await channel.send(log_message)

async def log_to_channel_vip(username, user_id, phone_number, count, execution_time):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        log_message = f"**SUPER** {username} ||{user_id}|| {phone_number} x**{count}** - {execution_time}\n"
        await channel.send(log_message)

def has_excluded_role(member):
    return discord.utils.get(member.guild.roles, id=1264997863079940170) in member.roles

@bot.event
async def on_ready():
    print(f'Kết nối thành công với {bot.user.name}')

def has_required_role(member):
    return discord.utils.get(member.guild.roles, id=ROLE_ID) in member.roles

async def add_and_remove_role(member):
    temp_role = discord.utils.get(member.guild.roles, id=TEMP_ROLE_ID)
    if temp_role:
        await member.add_roles(temp_role)
        await asyncio.sleep(30)
        await member.remove_roles(temp_role)
        channel = bot.get_channel(ALLOWED_CHANNEL_ID)
        if channel:
            ping_message = await channel.send(f'{member.mention}')
            await asyncio.sleep(1)
            await ping_message.delete()
            embed = discord.Embed(
                title="⏳ Thời chờ đã hết!",
                description=f"{member.mention} hãy phát quà tiếp nào!",
                color=discord.Color.red()
            )
            embed.set_footer(text="Made by Th1nK")
            await channel.send(embed=embed)

async def add_and_remove_role_vip(member):
    temp_role = discord.utils.get(member.guild.roles, id=TEMP_ROLE_ID)
    if temp_role:
        await member.add_roles(temp_role)
        await asyncio.sleep(15)
        await member.remove_roles(temp_role)
        channel = bot.get_channel(VIP_CHANNEL_ID)
        if channel:
            ping_message = await channel.send(f'{member.mention}')
            await asyncio.sleep(1)
            await ping_message.delete()
            embed = discord.Embed(
                title="⏳ Thời chờ đã hết!",
                description=f"{member.mention} hãy phát quà tiếp nào!",
                color=discord.Color.red()
            )
            embed.set_footer(text="Made by Th1nK")
            await channel.send(embed=embed)


def check_permissions(ctx):
    if ctx.command.name == 'help':  # Không kiểm tra quyền cho lệnh /help
        return True, None
    if ctx.guild.id != ALLOWED_GUILD_ID:
        return False, 'Bot chỉ hoạt động tại server Al1nK SMS.'
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return False, f'Sms chỉ hoạt động tại kênh <#{ALLOWED_CHANNEL_ID}>.'
    if not has_required_role(ctx.author):
        return False, 'Bạn không có quyền sử dụng lệnh này.'
    return True, None

def validate_phone_number(phone_number):
    if len(phone_number) < 10:
        return False, "Số điện thoại không hợp lệ, hãy kiểm tra lại."
    elif len(phone_number) > 10:
        return False, "Số điện thoại không hợp lệ, hãy kiểm tra lại."
    return True, None

@bot.command()
async def sms(ctx, phone_number: str, count: int = 1):
    if has_excluded_role(ctx.author):
        await ctx.send("Đang trong thời gian chờ, dùng tiếp sau nhaa.")
        return

    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.send(f'Sms chỉ hoạt động tại kênh <#{ALLOWED_CHANNEL_ID}>.')
        return

    is_allowed, message = check_permissions(ctx)
    if not is_allowed:
        await ctx.send(message)
        return

    prev_sdt = phone_number  # Initialize prev_sdt with the current phone number

    # Check if the specific phone number already has a running process
    if (ctx.author.id, phone_number) in processes:
        embed = Embed(
            title="Tiến trình đang hoạt động",
            description=(
                f'💼 Tiến trình spam đến số **{prev_sdt}** vẫn đang hoạt động.\n'
                f'⌚ Hãy chờ tiến trình kết thúc trước khi tạo tiến trình mới.\n'
                f'🛠️ Hoặc dùng **/smsstop {prev_sdt}** để dừng tiến trình đó.'
            ),
            color=0xf78a8a  # Màu đỏ cho thông báo lỗi
        )
        embed.set_footer(text="Made By Th1nK")
        await ctx.message.reply(embed=embed, mention_author=False)
        return

    # Check if any other process by the user is still running
    running_process = next(((user_id, phone) for (user_id, phone), proc in processes.items() if user_id == ctx.author.id), None)
    if running_process:
        prev_sdt = running_process[1]  # Update prev_sdt with the phone number of the running process
        
        embed = Embed(
            title="Tiến trình đang hoạt động",
            description=(
                f'💼 Tiến trình spam đến số **{prev_sdt}** vẫn đang hoạt động.\n'
                f'⌚ Hãy chờ tiến trình kết thúc trước khi tạo tiến trình mới.\n'
                f'🛠️ Hoặc dùng **/smsstop {prev_sdt}** để dừng tiến trình đó.'
            ),
            color=0xf78a8a  # Màu đỏ cho thông báo lỗi
        )
        embed.set_footer(text="Made By Th1nK")
        await ctx.message.reply(embed=embed, mention_author=False)
        return

    is_valid, message = validate_phone_number(phone_number)
    if not is_valid:
        await ctx.send(message)
        return

    if ctx.channel.id == VIP_CHANNEL_ID:
        await ctx.send('Lệnh này không thể sử dụng ở kênh SUPER. Hãy dùng /supersms.')
        return

    special_role = discord.utils.get(ctx.guild.roles, id=SPECIAL_ROLE_ID)
    if not phone_number.isnumeric() or (phone_number in INVALID_NUMBERS and special_role not in ctx.author.roles):
        await ctx.send('Số không hợp lệ hoặc không được phép.')
        return

    if count < 1:
        await ctx.send('Số lần lặp phải >0')
        return

    if count > 10 :
        await ctx.send('Số lần lặp phải ≤10. Nhiều lần hơn hãy dùng /supersms.')
        return

    try:
        file_path = os.path.join(os.getcwd(), "sms.py")
        proc = await asyncio.create_subprocess_exec("python", file_path, phone_number, str(count))
        processes[(ctx.author.id, phone_number)] = proc

        username = ctx.author.name
        user_id = ctx.author.id
        execution_time = TimeStamp()

        await log_to_channel(username, user_id, phone_number, count, execution_time)
        
        embed = discord.Embed(
            title="🎉 Gửi Yêu Cầu Thành Công! 🎉",
            color=0xf78a8a
        )
        
        if count == 1:
            embed.add_field(
                name="Thông tin yêu cầu:",
                value=(
                    f"📞 **Thuê bao thụ thưởng:** {phone_number}\n"
                    f"💸 **Gói:** FREE\n"
                    f"⚡ **Tốc độ:** Thường\n"
                    f"🔗 **Số API:** 36\n"
                    f"⛓️ **Số lần lặp:** {count} lần (Mặc Định, MAX 10)\n"
                    f"⏳ **Thời gian hồi:** 30 giây"
                ),
                inline=False
            )
        else:
            embed.add_field(
                name="Thông tin yêu cầu:",
                value=(
                    f"📞 **Thuê bao thụ thưởng:** {phone_number}\n"
                    f"💸 **Gói:** FREE\n"
                    f"⚡ **Tốc độ:** Thường\n"
                    f"🔗 **Số API:** 36\n"
                    f"⛓️ **Số lần lặp:** {count} lần (MAX 10)\n"
                    f"⏳ **Thời gian hồi:** 30 giây"
                ),
                inline=False
            )
        embed.set_footer(text=f"Thời gian : {TimeStamp()}")
        embed.set_image(url=get_random_gif_url())

        await ctx.message.reply(embed=embed, mention_author=False)

        await add_and_remove_role(ctx.author)
    except Exception as e:
        await ctx.send(f'Đã xảy ra lỗi khi xử lý lệnh: {e}')
    finally:
        # Xóa tiến trình khỏi từ điển khi kết thúc
        if (ctx.author.id, phone_number) in processes:
            proc = processes[(ctx.author.id, phone_number)]
            try:
                await proc.wait()  # Chờ tiến trình kết thúc
            except Exception as e:
                print(f"Đã xảy ra lỗi khi dừng tiến trình: {e}")
            finally:
                processes.pop((ctx.author.id, phone_number), None)



@bot.command()
async def supersms(ctx, phone_number: str, count: int = 1):
    if has_excluded_role(ctx.author):
        await ctx.send("Đang trong thời gian chờ, dùng tiếp sau nhaa.")
        return

    # Kiểm tra kênh
    if ctx.channel.id != VIP_CHANNEL_ID:
        await ctx.send(f'Supersms chỉ hoạt động tại kênh <#{VIP_CHANNEL_ID}>.')
        return

    prev_sdt = phone_number  # Initialize prev_sdt with the current phone number

    # Check if the specific phone number already has a running process
    if (ctx.author.id, phone_number) in processes:
        embed = Embed(
            title="Tiến trình đang hoạt động",
            description=(
                f'💼 Tiến trình spam đến số **{prev_sdt}** vẫn đang hoạt động.\n'
                f'⌚ Hãy chờ tiến trình kết thúc trước khi tạo tiến trình mới.\n'
                f'🛠️ Hoặc dùng **/smsstop {prev_sdt}** để dừng tiến trình đó.'
            ),
            color=0xf78a8a  # Màu đỏ cho thông báo lỗi
        )
        embed.set_footer(text="Made By Th1nK")
        await ctx.message.reply(embed=embed, mention_author=False)
        return

    # Check if any other process by the user is still running
    running_process = next(((user_id, phone) for (user_id, phone), proc in processes.items() if user_id == ctx.author.id), None)
    if running_process:
        prev_sdt = running_process[1]  # Update prev_sdt with the phone number of the running process
        
        embed = Embed(
            title="Tiến trình đang hoạt động",
            description=(
                f'💼 Tiến trình spam đến số **{prev_sdt}** vẫn đang hoạt động.\n'
                f'⌚ Hãy chờ tiến trình kết thúc trước khi tạo tiến trình mới.\n'
                f'🛠️ Hoặc dùng **/smsstop {prev_sdt}** để dừng tiến trình đó.'
            ),
            color=0xf78a8a  # Màu đỏ cho thông báo lỗi
        )
        embed.set_footer(text="Made By Th1nK")
        await ctx.message.reply(embed=embed, mention_author=False)
        return

    # Kiểm tra vai trò
    if not discord.utils.get(ctx.author.roles, id=VIP_ROLE_ID):
        await ctx.send('Bạn cần ROLE SUPER để sử dụng lệnh này.')
        return

    is_valid, message = validate_phone_number(phone_number)
    if not is_valid:
        await ctx.send(message)
        return

    # Kiểm tra số điện thoại
    special_role = discord.utils.get(ctx.guild.roles, id=SPECIAL_ROLE_ID)
    if not phone_number.isnumeric() or (phone_number in INVALID_NUMBERS and special_role not in ctx.author.roles):
        await ctx.send('Số không hợp lệ hoặc không được phép.')
        return

    if count < 1:
        await ctx.send('Số lần lặp phải >0')
        return

    if count > 1000 :
        await ctx.send('Số lần lặp phải ≤1000, không là **nổ** bot bạn yêu ơi.')
        return

    try:
        file_path = os.path.join(os.getcwd(), "smsvip.py")
        # Chuyển count thành chuỗi
        proc = await asyncio.create_subprocess_exec("python", file_path, phone_number, str(count))
        processes[(ctx.author.id, phone_number)] = proc

        username = ctx.author.name
        user_id = ctx.author.id
        execution_time = TimeStamp()

        await log_to_channel_vip(username, user_id, phone_number, count, execution_time)

        embed = discord.Embed(
            title="🎉 Gửi Yêu Cầu Thành Công! 😈",
            color=0xf78a8a
        )
        
        if count == 1:
            embed.add_field(
                name="Thông tin yêu cầu:",
                value=(
                    f"📞 **Thuê bao thụ thưởng:** {phone_number}\n"
                    f"💸 **Gói:** SUPER\n"
                    f"⚡ **Tốc độ:** PLUS\n"
                    f"🔗 **Số API:** >100 (MAX)\n"
                    f"⛓️ **Số lần lặp:** {count} lần (Mặc Định, MAX 1000)\n"
                    f"⏳ **Thời gian hồi:** 15 giây"
                ),
                inline=False
            )
        else:
            embed.add_field(
                name="Thông tin yêu cầu:",
                value=(
                    f"📞 **Thuê bao thụ thưởng:** {phone_number}\n"
                    f"💸 **Gói:** SUPER\n"
                    f"⚡ **Tốc độ:** PLUS\n"
                    f"🔗 **Số API:** >100 (MAX)\n"
                    f"⛓️ **Số lần lặp:** {count} lần (MAX 1000)\n"
                    f"⏳ **Thời gian hồi:** 15 giây"
                ),
                inline=False
            )
        embed.set_footer(text=f"Thời gian : {TimeStamp()}")
        embed.set_image(url=get_random_gif_url())

        await ctx.message.reply(embed=embed, mention_author=False)

        await add_and_remove_role_vip(ctx.author)
    except Exception as e:
        await ctx.send(f'Đã xảy ra lỗi khi xử lý lệnh: {e}')
    finally:
        # Xóa tiến trình khỏi từ điển khi kết thúc
        if (ctx.author.id, phone_number) in processes:
            proc = processes[(ctx.author.id, phone_number)]
            try:
                await proc.wait()  # Chờ tiến trình kết thúc
            except Exception as e:
                print(f"Đã xảy ra lỗi khi dừng tiến trình: {e}")
            finally:
                processes.pop((ctx.author.id, phone_number), None)

@bot.command()
async def help(ctx):
    is_allowed, message = check_permissions(ctx)
    if not is_allowed:
        await ctx.send(message)
        return

    embed = discord.Embed(
        title="Danh Sách Lệnh",
        color=0xf78a8a
    )
    embed.add_field(name="/sms {số điện thoại} {số lần}", value="Gửi tin nhắn SMS.", inline=False)
    embed.add_field(name="/supersms {số điện thoại} {số lần}", value="Gửi tin nhắn SUPERSMS. (Cần có role SUPER, mua liên hệ Admin Th1nK)", inline=False)
    embed.add_field(name="/smsstop {số điện thoại}", value="Dừng tiến trình SpamSMS tới sdt đó.", inline=False)
    embed.add_field(name="/help", value="Xem danh sách lệnh hiện có.", inline=False)
    embed.set_footer(text="Made by Th1nK")

    await ctx.send(embed=embed)

@bot.command()
async def smsstop(ctx, phone_number: str):
    if ctx.channel.id not in [ALLOWED_CHANNEL_ID, VIP_CHANNEL_ID]:
        await ctx.send(f"Không dùng lệnh tại đây.")
        return

    if len(phone_number) >= 8:
        masked_number = phone_number[:6] + 'xxxx'
    else:
        masked_number = phone_number

    if (ctx.author.id, phone_number) in processes:
        proc = processes[(ctx.author.id, phone_number)]
        try:
            proc.kill()
            del processes[(ctx.author.id, phone_number)]
            embed = Embed(
                title="Dừng tiến trình thành công ✅",
                description=(
                    f'Đã dừng tiến trình spam tới số: **{masked_number}**.\n'
                ),
                color=0xf78a8a  # Màu đỏ cho thông báo lỗi
            )
            embed.set_footer(text="Made By Th1nK")
            await ctx.message.reply(embed=embed, mention_author=False)
        except Exception:
            embed = Embed(
                title="Không tìm thấy tiến trình ❓",
                description=(
                    f'Không tìm thấy tiến trình spam đến số: **{masked_number}**.\n'
                ),
                color=0xf78a8a  # Màu đỏ cho thông báo lỗi
            )
            embed.set_footer(text="Made By Th1nK")
            await ctx.message.reply(embed=embed, mention_author=False)
    else:
        embed = Embed(
            title="Không tìm thấy tiến trình ❓",
            description=(
                f'Không tìm thấy tiến trình spam đến số: **{masked_number}**.\n'
            ),
            color=0xf78a8a  # Màu đỏ cho thông báo lỗi
        )
        embed.set_footer(text="Made By Th1nK")
        await ctx.message.reply(embed=embed, mention_author=False)



@bot.command()
@commands.has_role(SPECIAL_ROLE_ID)  # Kiểm tra người dùng có vai trò admin không
async def stopall(ctx):
    if not discord.utils.get(ctx.author.roles, id=SPECIAL_ROLE_ID):
        await ctx.send("Bạn không có quyền sử dụng lệnh này.")
        return

    if not processes:
        await ctx.send("True - 0")
        return

    # Tạo danh sách các tiến trình để lặp qua
    processes_list = list(processes.items())

    for (user_id, phone_number), proc in processes_list:
        try:
            proc.terminate()  # Kết thúc tiến trình
            await proc.wait()  # Chờ tiến trình kết thúc
        except Exception as e:
            print(f"Đã xảy ra lỗi khi dừng tiến trình {user_id} - {phone_number}: {e}")
        finally:
            processes.pop((user_id, phone_number), None)

    await ctx.send("True - 1")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.guild and message.guild.id != ALLOWED_GUILD_ID:
        return

    # Kiểm tra nếu tin nhắn bắt đầu bằng lệnh
    if message.content.startswith('/'):
        # Kiểm tra nếu lệnh không phải là /sms hoặc /help
        if not (message.content.startswith('/sms') or message.content.startswith('/supersms') or message.content.startswith('/help') or message.content.startswith('/smsstop') or message.content.startswith('/stopall')):
            if message.channel.id != ALLOWED_CHANNEL_ID:
                await message.channel.send(f'Sai cú pháp, /help để xem chi tiết lệnh.')
                return

        # Xử lý lệnh
        await bot.process_commands(message)
    elif isinstance(message.channel, discord.DMChannel):
        await message.channel.send('Bot chỉ hoạt động tại server Al1nK SMS.')

bot.run(TOKEN)
