import datetime
import json
import re
import time
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

FRIDAY = 4
MONDAY = 0


class Crawler:
    def __init__(self, driver, debug=False):
        self.driver = driver
        self.id = 0

        self.driver.get("http://wilma.espoo.fi")
        self.driver.set_window_size(960, 1080)
        self.debug = debug

    def login(self, username, password):
        time.sleep(1)
        usernameField = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, "login-frontdoor")))
        usernameField.clear()
        time.sleep(0.1)
        usernameField.send_keys(username)

        time.sleep(0.1)

        passwordField = self.driver.find_element_by_id("password")
        passwordField.clear()
        passwordField.send_keys(password)

        time.sleep(0.1)

        elem = self.driver.find_element_by_name("submit")
        elem.send_keys(Keys.RETURN)

    @staticmethod
    def __filter_duplicates(elements):
        seen = set()
        def iteration (item):
            if item.text in seen:
                return False
            else:
                seen.add(item.text)
                return True

        return list(filter(iteration, elements))

    def get_schedule(self):
        self.driver.get("http://wilma.espoo.fi/schedule")
        next = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "vismaicon-arrow-right-circle")))
        next.click()
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "info")))
        # lessons = WebDriverWait(self.driver, 30).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "info")))
        range = self.__get_date_range()

        lessons = self.driver.find_elements_by_class_name("info")
        lessons = self.__filter_duplicates(lessons)
        details = list(map(self.__get_lesson_details, lessons))

        courses = set(map(lambda lesson: lesson.find_element_by_tag_name("a").text, lessons))
        print(courses, range, details)
        return Schedule(courses, range, details)

    def __get_lesson_details(self, lesson_element):
        course_title = lesson_element.find_element_by_class_name("no-underline-link")
        teacher = lesson_element.find_element_by_class_name("teachers")
        room = lesson_element.find_element_by_class_name("rooms")

        # print(course_title.text, teacher.text, room.text)
        details = self.__get_course_details(course_title)

        return course_title.text, teacher.text, room.text, details

    def __get_course_details(self, course_element):
        course_element.click()
        self.driver.switch_to.window(self.driver.window_handles[-1])
        tables = WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "table")))
        # print(tables)

        homework = []
        lesson_diary = []

        for table in tables:
            try:
                headers = list(map(lambda a: a.text, table.find_element_by_tag_name("thead").find_element_by_tag_name("tr").find_elements_by_tag_name("th")))
                # print(headers)

                if headers[1].lower().strip() == "kotitehtävät":
                    # print("Homework found!")
                    # homework
                    entries = table.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")

                    for entry in entries:
                        date, exercises = map(lambda x: x.text, entry.find_elements_by_tag_name("td"))
                        homework.append({"date": date, "exercises": exercises})

                elif headers[1].lower().strip() == "tuntinro":
                    # print("Diary found!")
                    # lesson diary
                    entries = table.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")
                    for entry in entries:
                        date, lesson_number, lesson_topic, teacher = map(lambda x: x.text, entry.find_elements_by_tag_name("td"))
                        lesson_diary.append({"date": date, "lesson_number": lesson_number, "lesson_topic": lesson_topic, "teacher": teacher})

            except:
                continue

        # self.driver.navigate().back()
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

        return homework, lesson_diary



    def __get_date_range(self):
        dates = self.driver.find_element_by_class_name("weekday-container").find_elements_by_class_name("weekday")
        return list(map(lambda x: x.text, dates))


    def __enter__(self):
        return self

    def __exit__(self, a, s, d):
        if not self.debug:
            self.driver.close()


def get_credentials(path="credentials"):
    with open(path) as file:
        return file.readlines()


@dataclass
class Lesson:
    nth_lesson: int
    day_of_week: int

def p(time_str):
    h, m = time_str.split(":")
    return 3600 * int(h) + 60 * int(m)


tuntikiertokaavio = {
    1: (Lesson(3, 1), Lesson(3, 3), Lesson(0, 4)),
    2: (Lesson(0, 0), Lesson(1, 2), Lesson(2, 3)),
    3: (Lesson(1, 0), Lesson(2, 2), Lesson(4, 3)),
    4: (Lesson(2, 1), Lesson(0, 2), Lesson(1, 4)),
    5: (Lesson(2, 0), Lesson(1, 1), Lesson(1, 3)),
    6: (Lesson(3, 0), Lesson(3, 2), Lesson(2, 4)),
    7: (Lesson(0, 1), Lesson(0, 3), Lesson(3, 4)),
    8: (Lesson(4, 0), Lesson(4, 2), Lesson(4, 4)),
}


def highlight(string):
    # return f"\u001b[40m\u001b[37;1m{string}\u001b[0m"
    return f"\u001b[1m{string}\u001b[0m"


class Schedule:
    lessonstarts = {
        0: " 8.30– 9.45 ",
        1: "10.00–11.15 ",
        2: "11.20–13.15 ",
        3: "13.30–14.45 ",
        4: "15.00–16.15 "
    }

    def __init__(self, courses, dates, details):
        self.schedule = [["" for weekday in range(5)] for nth_lesson in range(5)]
        self.dates = self.__parse_dates(dates)
        self.details = details
        for course in courses:
            palkki, title = course.split(": ")

            for timestamp in tuntikiertokaavio[int(palkki)]:
                self.schedule[timestamp.nth_lesson][timestamp.day_of_week] = title

    def __str__(self):
        highlight_date = self.get_highlight_date()

        first_row = [12 * " ", *[self.__pad(date) for date in self.dates]]
        first_row[highlight_date + 1] = highlight(first_row[highlight_date + 1])
        lines = [" ".join(first_row)]
        lines.append(12 * " " + ("+" + "-" * 10) * 5)
        # lines = []
        for index, row in enumerate(self.schedule):
            line = []
            line.append(self.lessonstarts[index])
            line.append("|")
            new_row = [self.__pad(item) for item in row]
            new_row[highlight_date] = highlight(new_row[highlight_date])
            line.append("|".join(new_row))
            lines.append("".join(line))

        return "\n".join(lines)

    def __pad(self, string):
        return string.rjust(9, " ") + " "

    def get_highlight_date(self):
        day_of_week = datetime.date.today().weekday()
        if day_of_week > FRIDAY:
            day_of_week = MONDAY

        return day_of_week

    weekdays = ("Ma", "Ti", "Ke", "To", "Pe")

    def __parse_dates(self, dates):
        today = datetime.date.today()
        dateobjects = []
        for date in dates:
            weekday, daymonth = re.sub("\\.$", "", date).split(" ")
            day, month = daymonth.split(".")

            if today.weekday() > FRIDAY:
                dateobjects.append(datetime.date(today.year, int(month), int(day)) + datetime.timedelta(days=7))
            else:
                dateobjects.append(datetime.date(today.year, int(month), int(day)) + datetime.timedelta(days=0))

        return [self.weekdays[index] + " " +  x for index, x in enumerate(list(map(lambda x: x.strftime("%d.%m"), dateobjects)))]

import transform_ugly

if __name__ == "__main__":
    options = Options()
    # options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)
    with Crawler(driver, debug=True) as crawler:
        crawler.login(*get_credentials())
        time.sleep(1)
        s = crawler.get_schedule()
        print(json.dumps(transform_ugly.transform(s.details, s), indent=4, sort_keys=True), file=open("out.json", "w"))
        # print(s, s.details)
