import httpx

from datetime import date, timedelta, datetime
from ansi import ansi, ansi_reset
from utility import async_wrap
import json

streams = {
    1849: "Д-11-1",
    1851: "Д-11-2",
    1848: "Д-11-3",
    1852: "Д-9-1",
    1850: "Д-9-2",
    1853: "Д-9-3",
    1847: "Д-9-4",
    1896: "ИСП-11-1",
    1926: "ИСП-11-2",
    1897: "ИСП-9-1",
    1922: "ИСП-9-2",
    1925: "ИСП-9-3",
    1919: "ПКС-9-4",
    1854: "ПСО-11-1",
    1890: "ПСО-11-2",
    1855: "ПСО-9-1",
    1856: "ПСО-9-2",
    1843: "ПСО-9-3",
    1858: "ПСОз-11-1",
    1857: "ПСОз-11-2",
    1846: "ПСОз-11-3",
    1842: "ПСОз-9-1",
    1859: "ПСОз-9-2",
    1860: "ПСОз-9-3",
    1845: "ПСОз-9-4",
    1899: "Р-11-1",
    1920: "Р-11-2",
    1930: "Р-11-3",
    1880: "Р-9-1",
    1898: "Р-9-2",
    1921: "Р-9-3",
    1929: "Р-9-4",
    1928: "Э-11-2",
    1900: "Э-9-1",
    1927: "Э-9-3"
}
streams_inverse = {v: k for k, v in streams.items()}

subgroups = {
    f"Д-11-1 (Дизайн [по отраслям])": ["Д-11-11а"],
    f"Д-11-2 (Дизайн [по отраслям])": ["Д-11-21а"],
    f"Д-11-3 (Дизайн [по отраслям])": ["Д-11-31а"],
    f"Д-9-1 (Дизайн [по отраслям])": ["Д-9-11а"],
    f"Д-9-2 (Дизайн [по отраслям])": ["Д-9-21а", "Д-9-21б"],
    f"Д-9-3 (Дизайн [по отраслям])": ["Д-9-31а"],
    f"Д-9-4 (Дизайн [по отраслям])": ["Д-9-41а"],
    f"ИСП-11-1 (Информационные системы и программирование)": ["ИСП-11-11а"],
    f"ИСП-11-2 (Информационные системы и программирование)": ["ИСП-11-21а"],
    f"ИСП-9-1 (Информационные системы и программирование)": ["ИСП-9-11а", "ИСП-9-12б"],
    f"ИСП-9-2 (Информационные системы и программирование)": ["ИСП-9-21а", "ИСП-9-22б"],
    f"ИСП-9-3 (Информационные системы и программирование)": ["ИСП-9-31а", "ИСП-9-31б"],
    f"ПКС-9-4 (Программирование в компьютерных системах)": ["ПКС-9-41а"],
    f"ПСО-11-1 (Право и организация социального обеспечения)": ["ПСО-11-11а", "ПСО-11-11б"],
    f"ПСО-11-2 (Право и организация социального обеспечения)": ["ПСО-11-21а"],
    f"ПСО-9-1 (Право и организация социального обеспечения)": ["ПСО-9-11а", "ПСО-9-11б"],
    f"ПСО-9-2 (Право и организация социального обеспечения)": ["ПСО-9-21а", "ПСО-9-21б"],
    f"ПСО-9-3 (Право и организация социального обеспечения)": ["ПСО-9-31а", "ПСО-9-32б"],
    f"ПСОз-11-1 (Право и организация социального обеспечения)": ["ПСОз-11-11а"],
    f"ПСОз-11-2 (Право и организация социального обеспечения)": ["ПСОз-11-21а"],
    f"ПСОз-11-3 (Право и организация социального обеспечения)": ["ПСОз-11-31а"],
    f"ПСОз-9-1 (Право и организация социального обеспечения)": ["ПСОз-9-11а"],
    f"ПСОз-9-2 (Право и организация социального обеспечения)": ["ПСОз-9-21а"],
    f"ПСОз-9-3 (Право и организация социального обеспечения)": ["ПСОз-9-31а"],
    f"ПСОз-9-4 (Право и организация социального обеспечения)": ["ПСОз-9-41а"],
    f"Р-11-1 (Реклама)": ["Р-11-11а"],
    f"Р-11-2 (Реклама)": ["Р-11-21а"],
    f"Р-11-3 (Реклама)": ["Р-11-31а"],
    f"Р-9-1 (Реклама)": ["Р-9-11а"],
    f"Р-9-2 (Реклама)": ["Р-9-21а"],
    f"Р-9-3 (Реклама)": ["Р-9-31а"],
    f"Р-9-4 (Реклама)": ["Р-9-41а"],
    f"Э-11-2 (Экономика и бухгалтерский учет [по отраслям])": ["Э-11-21а"],
    f"Э-9-1 (Экономика и бухгалтерский учет [по отраслям])": ["Э-9-11а"],
    f"Э-9-3 (Экономика и бухгалтерский учет [по отраслям])": ["Э-9-31а"]
}

week_ordinal = {
    "Понедельник": 0,
    "Вторник": 1,
    "Среда": 2,
    "Четверг": 3,
    "Пятница": 4,
    "Суббота": 5,
}
week_ordinal_inverse = {v: k for k, v in week_ordinal.items()}

def get_week_start(desired_date, ret_obj = False):
    if desired_date != "current":
        today = datetime.strptime(desired_date, "%d.%m.%Y").date()
    else:
        today = date.today() + timedelta(days=1)
    start = today - timedelta(days=today.weekday())

    if ret_obj:
        return start

    return start.strftime('%d.%m.%Y')

def get_week_end(desired_date, ret_obj = False):
    if desired_date != "current":
        today = datetime.strptime(desired_date, "%d.%m.%Y").date()
    else:
        today = date.today() + timedelta(days=1)
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    if ret_obj:
        return end

    return end.strftime('%d.%m.%Y')

def get_lessons(stream, term, date = "current"):
    response = httpx.post("https://psi.thinkery.ru/shedule/public/public_getsheduleclasses_spo", data = {
        "studyyear_id": 25, # год + 1?
        "stream_id": stream, # поток
        "term": term, # семестр
        "start_date": get_week_start(date),
        "end_date": get_week_end(date)
    })

    return json.loads(response.text)

@async_wrap
def get_lessons_async(stream, term, date = "current"):
    return get_lessons(stream, term, date)

def get_formatted_lessons(lessons, subgroup = None, output_teachers = False, date = "current"):
    sorted_lessons = [{}] * 6

    week_start = get_week_start(date, ret_obj = True)

    for lesson in lessons:
        weekday_name = lesson.get("weekday_name") # день недели (Понедельник, Вторник и т.д)
        daytime_ord = lesson.get("daytime_ord") # номер лекции
        daytime_start = lesson.get("daytime_start") # начало лекции (просто текст по типу 14:00)
        daytime_end = lesson.get("daytime_end") # конец лекции (просто текст по типу 15:30)
        subgroup_name = lesson.get("subgroup_name") # подгруппа
        teacher_fio = lesson.get("teacher_fio") # фио преподавателя
        discipline_name = lesson.get("discipline_name") # предмет
        cabinet_number = lesson.get("cabinet_number") # кабинет (может заменяться нами на ск или что-то другое)
        stream_id = lesson.get("stream_id") # номер потока
        classtype_id = lesson.get("classtype_id") # тип занятия
        building_name = lesson.get("building_name") # здание (главный корпус, спортивный комплекс или что-то другое)
        date_start = lesson.get("date_start_text")

        # https://psi.thinkery.ru/shedule/public/public_shedule_spo_grid -> raw response -> примерно на строчках 200
        if classtype_id not in [1,2,3,4] and (subgroup != None and subgroup_name != subgroup):
            continue

        week_offset = week_ordinal.get(weekday_name)

        if not sorted_lessons[week_offset]:
            sorted_lessons[week_offset] = [{}] * 7
        
        if building_name != "Главный корпус":
            cabinet_number = building_name
        
        corrected_daytime_ord = int(daytime_ord) - 1

        if corrected_daytime_ord < 0 or corrected_daytime_ord > 6:
            continue
        
        sorted_lessons[week_offset][corrected_daytime_ord] = {
            "daytime_start": daytime_start,
            "daytime_end": daytime_end,
            "teacher_fio": teacher_fio,
            "discipline_name": discipline_name,
            "cabinet_number": cabinet_number
        }
    
    output = ""

    names = []

    for i in range(len(sorted_lessons)):
        day = sorted_lessons[i]

        output += f"[{(week_start + timedelta(days=i)).strftime('%d.%m.%Y')}] {week_ordinal_inverse[i]}: \n"

        for j in range(len(day)):
            lesson = day[j]

            if not lesson.get('discipline_name'):
                output += f"\t{j + 1}: ...\n"
                continue
            
            output += f"\t{j + 1}: [{lesson.get('cabinet_number')}] {lesson.get('discipline_name', '...')} ({lesson.get('daytime_start')} - {lesson.get('daytime_end')}) \n"

            names.append(f"{lesson.get('discipline_name')}: {lesson.get('teacher_fio')}")

        if len(day) <= 0:
            output += "\tЛекций нет.\n"
            
        output += "\n"
    
    if output_teachers:
        names = set(names)
        for line in names:
            output += line + "\n"
    
    return output

#lessons = get_lessons(stream = 1897, term = 2)

#print(get_formatted_lessons(lessons = lessons, subgroup = "ИСП-9-11а", output_teachers = False))