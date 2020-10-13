import json
import random
import string
from pprint import pprint

from Crawler import Schedule


def transform_upcoming(schedule, rooms_temp):
    upcoming = {}

    dates = schedule.dates
    for nth_lesson, row in enumerate(schedule.schedule):
        for day_of_week, course_title in enumerate(row):
            date = dates[day_of_week]
            
            if course_title == "":
                continue

            time = Schedule.lessonstarts[nth_lesson]

            start_time, end_time = map(convert_time, time.split("–"))

            if convert_date(date) in upcoming:
                upcoming[convert_date(date)].append({
                    "type": "lesson",
                    "start_time": start_time,
                    "end_time": end_time,
                    "course": course_title,
                    "room": rooms_temp[course_title]
                })
            else:
                upcoming[convert_date(date)] = [{
                    "type": "lesson",
                    "start_time": start_time,
                    "end_time": end_time,
                    "course": course_title,
                    "room": rooms_temp[course_title]
                }]

    return upcoming


def convert_time(time):
    return time.strip().replace(".", ":")

def transform(schedule):
    courses_ugly = schedule.details

    teachers = {}
    courses = {}

    rooms_temp = {}

    for entry in courses_ugly:
        course_title = entry[0].split(": ")[1]
        teacher_name_short = entry[1]
        course_teacher = {
                             "long_name": "",
                             "short_name": teacher_name_short,
                             "role": "",
                             "email": ""
                         }

        if course_teacher not in teachers.values():
            teachers[teacher_name_short] = course_teacher

        homework_ugly = entry[3][0]
        lesson_diary_ugly = entry[3][1]

        rooms_temp[course_title] = entry[2]

        homework = []
        for ugly in homework_ugly:
            homework.append({
                "given_on": convert_date(ugly["date"]),
                "homework": ugly["exercises"]
            })

        lesson_diary = []
        for ugly in lesson_diary_ugly:
            lesson_diary.append({
                "lesson_number": ugly["lesson_number"],
                "lesson_topic": ugly["lesson_topic"],
                "date": convert_date(ugly["date"])
            })

        courses[course_title] = {
            "title": course_title,
            "teacher": teacher_name_short,
            "homework": homework,
            "lesson_diary": lesson_diary
        }

    upcoming = transform_upcoming(schedule, rooms_temp)
    # print(courses, teachers)
    # pprint(courses, compact=False)
    # pprint(teachers)

    return {
        "courses": courses,
        "teachers": teachers,
        "upcoming": upcoming
    }




def convert_date(date):
    if len(date.split(" ")) > 1:
        return f'2020-{"-".join(date.split(" ")[1].split(".")[::-1])}'
    else:
        return "-".join(date.split(".")[::-1])




def get_random_hash(length):
    return f"${''.join(random.choices(string.digits, k=length))}"


if __name__ == "__main__":
    d = [('3: MAA18.1', 'KAA', '2240', ([], [])), ('5: MAA07.D2', 'SAV', '1317', ([{'date': '08.10.2020', 'exercises': '134, 140, 148'}, {'date': '06.10.2020', 'exercises': '109, 115, 118, 119, 120'}, {'date': '05.10.2020', 'exercises': 'Yhdistetty funktio moniste classroomissa t. 3 ja 5 sekä kirjasta 401, 404, 415'}], [{'date': '08.10.2020', 'lesson_number': '', 'lesson_topic': '', 'teacher': 'Ville Saarikivi'}, {'date': '06.10.2020', 'lesson_number': '', 'lesson_topic': '', 'teacher': 'Ville Saarikivi'}, {'date': '05.10.2020', 'lesson_number': '', 'lesson_topic': '', 'teacher': 'Ville Saarikivi'}])), ('6: FY10.D2', 'MAK', '1317', ([], [])), ('7: KE06.D2', 'HON', '2313', ([{'date': '09.10.2020', 'exercises': 'Classroom-koodi: 4qj54za Tunnin korvaava tehtävä löytyy Classroomista! (jos olit poissa)'}, {'date': '08.10.2020', 'exercises': 'Classroom-koodi: 4qj54za Tunnin korvaava tehtävä löytyy Classroomista! (jos olit poissa)'}], [{'date': '09.10.2020', 'lesson_number': '', 'lesson_topic': 'Tuntemattomat jauheet', 'teacher': 'Maija Honkela'}, {'date': '08.10.2020', 'lesson_number': '', 'lesson_topic': 'Maissinjyvän höyrynpaine', 'teacher': 'Maija Honkela'}])), ('4: UE02.3', 'KAE', '1118', ([{'date': '09.10.2020', 'exercises': 'Kpl 2.2 tehtävä EK1'}, {'date': '07.10.2020', 'exercises': 'Kpl 2.1 tehtävä EK1'}, {'date': '06.10.2020', 'exercises': 'Kpl 1 tehtävä EK1'}], [{'date': '09.10.2020', 'lesson_number': '3', 'lesson_topic': 'Keskiajan kristillisyys', 'teacher': 'Emma Karjalainen'}, {'date': '07.10.2020', 'lesson_number': '2', 'lesson_topic': 'Kristinuskon synty ja varhaisvaiheet', 'teacher': 'Emma Karjalainen'}, {'date': '06.10.2020', 'lesson_number': '1', 'lesson_topic': 'Aloitus', 'teacher': 'Emma Karjalainen'}])), ('1: ENA04.7', 'PiV', '2240', ([{'date': '09.10.2020', 'exercises': 'Topic 1 exercise 1f (translation sentences). Grammar/Nationality words exercise 36 (found in the GRAMMAR section of your book).'}, {'date': '08.10.2020', 'exercises': 'Topic 1: Exercises 1b and 1c.'}, {'date': '06.10.2020', 'exercises': 'Exercise 3 "Fill in the missing words" in section "Learning to learn" / "4. Using signposts "(this section can be found after the texts in your digital book, before the Grammar section). Page 130 in the paperback book.'}], [{'date': '09.10.2020', 'lesson_number': '', 'lesson_topic': 'Topic 1 exercises 1e, 1h. Vocabulary revision 1.1. Grammar: Nationality words + exercise 34.', 'teacher': 'Virva Pitsinki'}, {'date': '08.10.2020', 'lesson_number': '', 'lesson_topic': 'Topic 1 engage discussion. Text 1 vocabulary, listen + translate + exercise 1a.', 'teacher': 'Virva Pitsinki'}, {'date': '06.10.2020', 'lesson_number': '', 'lesson_topic': 'Course introduction (material in Google Classroom). Using Signposts (digital book Learning to learn/4.Using signposts, paperback book p. 128-129) + exercises 2 & 5. Charity work discussion (material in Google Classroom).', 'teacher': 'Virva Pitsinki'}]))]
    schedule = Schedule({'5: MAA07.D2', '1: ENA04.7', '4: UE02.3', '7: KE06.D2', '6: FY10.D2', '3: MAA18.1'}, ['Ma 19.10.', 'Ti 20.10.', 'Ke 21.10.', 'To 22.10.', 'Pe 23.10.'], d)
    print(schedule)
    print(json.dumps(transform(schedule), indent=4))