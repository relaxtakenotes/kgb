import discord

from schedule import get_lessons_async, get_formatted_lessons, streams_inverse, get_week_start, get_week_end, subgroups
from utility import textwrap, write_internal, get_internal, get_text_difference
from ansi import ansi, ansi_reset, ansi_wrap

config = None
client = None

commands = {
    "user": {},
    "admin": {}
}

def register_cmd(func, func_name, typee, description="No description."):
    if typee == "admin":
        commands["admin"][func_name] = [func, description]
    elif typee == "user":
        commands["user"][func_name] = [func, description]

async def handle_admin_commands(message):
    if isinstance(message.channel, discord.DMChannel) or not message.author.guild_permissions.administrator:
        return

    _split = message.content.replace(config["prefix"], "").split()
    args = _split[1:]
    cmd = _split[0]

    if commands["admin"].get(cmd):
        async with message.channel.typing():
            await commands["admin"][cmd][0](message, args)

async def handle_user_commands(message):
    _split = message.content.replace(config["prefix"], "").split()
    args = _split[1:]
    cmd = _split[0]

    if commands["user"].get(cmd):
        async with message.channel.typing():
            await commands["user"][cmd][0](message, args)

async def cmd_help(message, args):
    response = "\n\nКоманды для админа:\n"
    for name, data in commands["admin"].items():
        response += f"\t{name} - {data[1]}\n"
    response += "\nКоманды для пользователей:\n"
    for name, data in commands["user"].items():
        response += f"\t{name} - {data[1]}\n"
    for block in textwrap(response):
        await message.channel.send(block)

async def cmd_get_schedule(message, args):
    stream_str = str(args[0])
    subgroup = str(args[1])
    output_teachers = str(args[2])

    if output_teachers == "да":
        output_teachers = True
    else:
        output_teachers = False
    
    target_day = "current"
    if len(args) > 3:
        target_day = args[3]

    lessons = await get_lessons_async(stream = streams_inverse.get(stream_str), term = config["term"], date = target_day)
    output = f"Расписание для группы {stream_str} ({subgroup}) [{get_week_start(target_day)} - {get_week_end(target_day)}] \n\n" + get_formatted_lessons(lessons = lessons, subgroup = subgroup, output_teachers = output_teachers, date = target_day)

    for block in textwrap(output):
        await message.channel.send(block)

async def cmd_get_streams(message, args):
    output = []

    for stream_name, substreams in subgroups.items():
        output.append(f"{stream_name}: {', '.join(substreams)}")

    for block in textwrap("\n".join(output)):
        await message.channel.send(block)

async def cmd_create_schedule_watcher(message, args):
    stream_str = str(args[0])
    subgroup = str(args[1])
    output_teachers = str(args[2])

    if output_teachers == "да":
        output_teachers = True
    else:
        output_teachers = False
    
    channel_id = message.channel.id

    data = get_internal()

    data[channel_id] = {
        "stream_str": stream_str,
        "subgroup": subgroup,
        "output_teachers": output_teachers,
        "last_schedule_string": ""
    }
    
    write_internal(data)

    await message.reply("Расписание появится в течении 5 минут, пока не настанет время обновлять данные всех расписаний.")

async def cmd_force_schedule_update(message, args):
    data = get_internal()

    for channel_id, watcher in data.items():
        channel = client.get_channel(int(channel_id))

        if not channel:
            continue

        lessons = await get_lessons_async(streams_inverse.get(watcher.get("stream_str")), config["term"])
        formatted = f"Расписание для группы {watcher.get('stream_str')} ({watcher['subgroup']}) [{get_week_start('current')} - {get_week_end('current')}] \n\n" + get_formatted_lessons(lessons, subgroup=watcher["subgroup"], output_teachers=watcher["output_teachers"])

        if formatted == watcher["last_schedule_string"]:
            continue

        diff = get_text_difference(watcher["last_schedule_string"], formatted)
        
        diff_count = 0

        output = ""

        for line in diff:
            if line.startswith("-"):
                output += ansi.normal.fg.red + line + ansi_reset + "\n"
                diff_count += 1
            elif line.startswith("+"):
                output += ansi.bold.fg.green + line + ansi_reset + "\n"
                diff_count += 1
            elif line.startswith("?"):
                pass
            else:
                output += line + "\n"
        
        if diff_count > 25: # 5 дней в неделю * 3 лекции в день (максимум 7) * 2 типа изменения (добавление и удаление линии) - 5 на всякий случай
            output = formatted

        await channel.send("@everyone")
        for block in ansi_wrap(output.strip()):
            await channel.send(block)

        data[channel_id]["last_schedule_string"] = formatted
    
    write_internal(data)

register_cmd(cmd_help, "помощь", "user", "Показывает все команды и доп. информацию.")
register_cmd(cmd_get_schedule, "расписание", "user", "Показывает расписание. (р.расписание 'группа' 'подгруппа' 'вывести_имена_учителей' 'день_отсчёта (в таком формате: 05.02.2024, можно не указывать)')")
register_cmd(cmd_get_streams, "потоки", "user", "Показывает все потоки/группы.")
register_cmd(cmd_create_schedule_watcher, "уведомления", "user", "Создаёт уведомления о расписании в определённый канал. (р.уведомления 'группа' 'подгруппа' 'вывести_имена_учителей')")

register_cmd(cmd_force_schedule_update, "обновить", "admin", "Принудительно обновляет расписания.")