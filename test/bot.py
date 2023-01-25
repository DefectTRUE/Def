import os
import disnake
import sqlite3
import random
import json
import datetime
import string
from tabulate import tabulate
import requests
import time
import asyncio
from disnake.ext import commands
from disnake.ext.commands import cooldown, BucketType
from PIL import Image, ImageFont, ImageDraw
import io
from io import BytesIO
from dislash import InteractionClient, ActionRow, Button, ButtonStyle
from inter import Interact





bot = commands.Bot(command_prefix = ">", intents = disnake.Intents.all())
bot.remove_command ('help' )






@bot.event
async def on_ready():
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        name TEXT,
        id INT,
        cash BIGINT,
        rep INT,
        lvl INT,
        xp INT,
        server_id
    )""")
    connection.commit()


    cursor.execute("""CREATE TABLE IF NOT EXISTS shop (
        role_id INT,
        id INT,
        cost BIGINT
    )""")  
    
    
    

    for guild in bot.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1, 0, {guild.id})")
            else:
                pass
            connection.commit()
    print("Bot connected")
    await bot.change_presence (status= disnake.Status.online, activity = disnake.Game ('капибару'))
    

@bot.event
async def on_member_join(member):
    if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1, 0, {member.guild.id})")
        connection.commit()
    else:
        pass






#Недоделано 
@bot.command(pass_context = True)
async def br(ctx):

    loose = (random.randint(1, 100))
    if loose >= 60:
        embeda = disnake.Embed(
        title = (f"Вы выиграли и получили: "),
        description = (f"test"),
        color = 0xFEE75C
        )
        await ctx.send(embed=embeda)
        amount = 2
        cursor.execute("UPDATE users SET cash = cash * 2 WHERE id = {}".format(amount, ctx.author.id))
    else:
        embedf = disnake.Embed(
        title = ("Коробка с наградами."),
        description = ("Вы проиграли"),
        color = 0xFEE75C
        )
        await ctx.send(embed=embedf)
        print(f"{loose}")    
    


@bot.command(aliases = ['add-shop'])
async def __add_shop (ctx, role: disnake.Role = None, cost: int = None):
        cursor.execute("INSERT INTO shop VALUES ({}, {}, {})".format(role.id, ctx.guild.id, cost))
        connection.commit()

@bot.command(aliases = ['remove-shop'])
async def __remove_shop (ctx, role: disnake.Role = None):
    cursor.execute("DELETE FROM shop WHERE role_id = {}".format(role.id))
    connection.commit()


@bot.command(aliases = ['shop'])
async def __shop(ctx):
    embed = disnake.Embed(title="**Магазин ролей**")

    for row in cursor.execute(f"SELECT role_id, cost FROM shop WHERE id = {ctx.guild.id}"):
        if ctx.guild.get_role(row[0]) is not None:
            embed.add_field(name = f"Стоимость **{row[1]} **:xcoincat:*", value = f"Вы приобретете роль {ctx.guild.get_role(row[0]).mention}", inline = False)
    await ctx.send(embed=embed)


@bot.command(aliases = ['buy-role'])
async def __buy (ctx, role: disnake.Role = None):
    if role is None:
        await ctx.send(f"**{ctx.author}, Укажите роль.")
    else:
        role_for_sale = cursor.execute("SELECT role_id FROM shop WHERE role_id = {}".format(role.id)).fetchone()
        if role_for_sale is None:
            await ctx.send(f"**{ctx.author}**, Роль не для продажи")
        elif role in ctx.author.roles:
            await ctx.send("f**{ctx.author}, У вас уже есть эта роль")
        else:
            cost = cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0]
            cash = cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]
            if cost > cash:
                await ctx.send(f"**{ctx.author}**, не хватает {cost-cash} монет")
            else:
                await ctx.author.add_roles(role)
                cursor.execute("UPDATE users SET cash = cash - {0} WHERE id = {1}".format(cost, ctx.author.id)) 
                connection.commit()
                await ctx.message.add_reaction('✅')


@bot.command()
async def transfer(ctx, recipient: disnake.User, amount: int):
    sender_id = ctx.author.id
    sender_cash = cursor.execute("SELECT cash FROM users WHERE id = {}".format(sender_id)).fetchone()[0]
    if sender_cash < amount:
        await ctx.send(f"**{ctx.author}**, У вас не хватает для перевода {amount} монет.")
    else:
        recipient_cash = cursor.execute("SELECT cash FROM users WHERE id = {}".format(recipient.id)).fetchone()[0]
        cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(amount, sender_id))
        cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, recipient.id))
        connection.commit()
        await ctx.send(f"**{ctx.author}** вы перевели {amount} для **{recipient}**.\n{ctx.author}'s Новый баланс: {sender_cash - amount}\n{recipient} Новый баланс: {recipient_cash + amount}")






@bot.event
async def on_message(message):
    if len(message.content) > 6:
        for row in cursor.execute(f"SELECT xp,lvl,cash FROM users WHERE id={message.author.id}"):
            expi=row[0]+random.randint(5, 40)
            cursor.execute(f'UPDATE users SET xp={expi} WHERE id={message.author.id}')
            lvch=expi/(row[1]*600)
            print(int(lvch))
            lv=int(lvch)
            if row[1] < lv:
                await message.channel.send(f"``Поздаляем {message.author.name} с достижением {lv} уровня!``")
                bal=500*lv
                cursor.execute(f'UPDATE users SET lvl={lv},cash={bal} WHERE id={message.author.id}')
    await bot.process_commands(message)
    connection.commit()

@bot.command()
async def account(ctx):
    table=[["name","cash","lvl","xp"]]
    for row in cursor.execute(f"SELECT name,cash,lvl,xp FROM users WHERE id={ctx.author.id}"):
        table.append([row[0],row[1],row[2],row[3]])
        await ctx.send(f">\n{tabulate(table)}")









@bot.command(aliases = ['balance'])
async def __balance(ctx, member: disnake.Member = None):
    if member is None:
        await ctx.send(embed = disnake.Embed(
            colour=0xFEE75C,
            description = f"""Баланс пользователя **{ctx.author}** составляет **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} ** <a:xcoincat:1001493260910469180>  """
            ))
    else:
        await ctx.send(embed = disnake.Embed(
            colour=0xFEE75C,
            description = f""" Баланс пользователя **{member}** составляет **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]}** <a:xcoincat:1001493260910469180>  """
            ))



@bot.command(aliases = ['timely'])
@commands.cooldown(1, 60*60*4, commands.BucketType.user)
async def __timely(ctx, amount: int = None):
        if amount is None:
         embed = disnake.Embed(
            description = f""" Вы получили свои **600** <:bg:1067836598038822962> . Вы сможете получить снова через 4ч. """,
            colour=0xFEE75C
            )

        embed.set_author(
        name=f"""{ctx.author.name}""",
        icon_url=f"""{ctx.author.avatar.url}"""
        )
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/763496900551901254/892525111234666506/ok.png")

        await ctx.send ( embed = embed )

        amount = 600  
        cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, ctx.author.id))
        connection.commit()

@__timely.error
async def command_timely_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = disnake.Embed(description=f"Вы уже получили свою награду. Вы сможете получить её заново через {error.retry_after:2f}s.", color=0xFEE75C)
        em.set_author(
        name=f"""{ctx.author.name}""",
        icon_url=f"""{ctx.author.avatar.url}"""
        )
        em.set_thumbnail(url="https://media.discordapp.net/attachments/763496900551901254/892528061646536794/strelka_spin_2.gif")

        await ctx.send(embed=em)


@bot.command(aliases = ['rob'])
@commands.cooldown(1, 60*60*8, commands.BucketType.user)
async def __rob(ctx, *arg, amount: int = None):
        if amount is None:
         await ctx.send(embed = disnake.Embed(
            description = f""" 👌⠀Вы успешно ограбили случайного пользователя на **1900** <:bg:1067836598038822962> . Повторная попытка будет доступна через 8ч.""",
            colour=0xFEE75C
         ))

        amount = 1900
        cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(int(amount), ctx.author.id))
        connection.commit()


@bot.command(aliases = ['award'])
async def __award (ctx, member: disnake.Member = None, amount: int=None):
    if member is None:
        await ctx.send(f"**{ctx.author}**, укажите пользователя, которому желаете выдать награду.")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author}**, укажите сумму которой желаете вознаградить пользователя.")
        elif amount <1:
            await ctx.send(f"**{ctx.author}**, укажите сумму которая превышает 1 <:bg:1067836598038822962> .")
        else:
            cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, member.id))

        connection.commit()
        await ctx.message.add_reaction('✅')



@bot.command()
async def fox(ctx):
    response = requests.get('https://some-random-api.ml/img/fox')
    json_data = json.loads(response.text)

    embed = disnake.Embed(color = 0xFEE75C, title = 'Случайная фотография лисы')
    embed.set_image(url = json_data['link']) 
    await ctx.send(embed = embed) 


@bot.command ( pass_context = True)
async def clear ( ctx, amount = 1):
    await ctx.channel.purge( limit = amount )



@bot.command(aliases = ['rep', '+rep'])
@commands.cooldown(1, 60*60*24, commands.BucketType.user)
async def __rep(ctx, member: disnake.Member = None):
    cursor.execute("UPDATE users SET rep = rep + {} WHERE id = {}".format(1, member.id))
    connection.commit()
    await ctx.send(embed = disnake.Embed(
    title= f"""{ctx.author}""",
    description = f"""Вы подняли {member.name} репутацию. Вы сможете сделать это снова через 24 часа""",
    colour=0x00
        ))


@__rep.error
async def command_rep_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        time = datetime.timedelta(seconds=error.retry_after)
        hour = time.seconds // 3600
        minute = (time.seconds // 60) % 60
    
        em = disnake.Embed(description=f"Вы уже выдали +rep одному из пользователей. Вы сможете снова использовать эту команду через {hour}:{minute}", color=0x2f3136)
        em.set_author(
        name=f"""{ctx.author.name}""",
        icon_url=f"""{ctx.author.avatar.url}"""
        )
        em.set_thumbnail(url="https://media.discordapp.net/attachments/763496900551901254/892528061646536794/strelka_spin_2.gif")

        await ctx.send(embed=em)

@bot.command(aliases = ['lb'])
async def __lb(ctx):
    embed = disnake.Embed(title = 'Топ 10 сервера')
    counter = 0

    for row in cursor.execute("SELECT name, cash FROM users WHERE server_id = {} ORDER BY cash DESC LIMIT 10".format(ctx.guild.id)):
        counter += 1
        colour=0xFEE75C
        embed.add_field(
            name = f'# {counter} |`{row[0]}`',
            value = f'{row[1]} <:bg:1067836598038822962>',
            inline = False
        )
    await ctx.send(embed = embed)



@bot.command(aliases = ['replb', 'rlb'])
async def __rlb(ctx):
    embed = disnake.Embed(title = 'Топ 10 сервера по репутации')
    counter = 0

    for row in cursor.execute("SELECT name, rep FROM users WHERE server_id = {} ORDER BY rep DESC LIMIT 10".format(ctx.guild.id)):
        counter += 1
        embed.add_field(
            name = f'# {counter} |`{row[0]}`',
            value = f'Кол-во репутации: {row[1]}',
            inline = False
        )
    await ctx.send(embed = embed)











@bot.command()
async def redpanda(ctx):
    response = requests.get('https://some-random-api.ml/img/red_panda')
    json_data = json.loads(response.text)

    embed = disnake.Embed(color = 0xFEE75C, title = 'Случайная фотография красной панды')
    embed.set_image(url = json_data['link']) 
    await ctx.send(embed = embed) 


@bot.command() 

async def profile(ctx, user: disnake.Member = None): 

    if user == None: 

        user = ctx.author 

        image = Image.open("banner.jpg") 

        img = image.resize((800, 392)) 

        idraw = ImageDraw.Draw(img) 

        title = ImageFont.truetype('Pwww.ttf', size = 30) 

        name = user.name 

        idraw.text((100, 170), name, font = title, fill = "white") 

        cash = f"""{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}  """

        idraw.text((100, 240), cash, font = title, fill = "white") 

        avatar = user.avatar.with_size(128).url 

        avt = BytesIO(await user.avatar.read()) 

        imga = Image.open(avt) 

        imguser = imga.resize((50, 50)) 

        img.paste(imguser, (80, 28)) 

        img.save("profile.jpg") 

        await ctx.send(file = disnake.File("profile.jpg"))

@bot.command()
async def rand(ctx, *arg):
    await ctx.reply(random.randint(1, 2))




connection = sqlite3.connect('server.db')
cursor = connection.cursor()



@bot.command( pass_context = True )
async def help( ctx ):
    
    emb = disnake.Embed ( title = 'Навигация по командам')
    colour=0xFEE75C
    emb.add_field ( name = '>clear', value = 'Очистка чата', inline=False)
    emb.add_field ( name = '>redpanda', value = 'Случайная фотография красной панды', inline=False)
    emb.add_field ( name = '>fox', value = 'Случайная фотография лисы', inline=False)
    emb.add_field ( name = '>balance', value = 'Ваш баланс', inline=False)
    emb.add_field ( name = '>timely', value = 'Раз в 8 часов вы можете просто так получить серверную валюту', inline=False)
    emb.add_field ( name = '>rob', value = 'Раз в 8 часов вы можете ограбить случайного пользователя', inline=False)
    emb.add_field ( name = '>award', value = 'Выдать серверную валюту', inline=False)


    await ctx.send ( embed = emb )























bot.run("MTA2NTM0NzQwMDIzNzA3NjU1MA.GOEswd.IR1xzNwMF7cgWUItPpqqmXfFb5Xl36N4BmXPJw")