from .models import *
from django.contrib.auth.models import User
import enum

class Semester(enum.Enum):
    Spring = 'SP'
    Summer = 'SU'
    Fall = 'FA'
    Winter = 'WI'

def save_user_course(course_schedule_id, user_id):
    course_schedule = CourseSchedule.objects.get(pk=course_schedule_id)
    user = User.objects.get(pk=user_id)

    sem_strs = course_schedule.term.split()
    term = Semester[sem_strs[0]]
    year = sem_strs[1]
    new_user_course = UserCourse(semester=term.value, year=year, status='PL', school_course_id=course_schedule.school_course_id, user_id=user_id)

    print(new_user_course.semester)

    existing_user_course = UserCourse.objects.filter(semester=new_user_course.semester,
                                                    year=new_user_course.year,
                                                    school_course_id=new_user_course.school_course_id,
                                                    user_id=new_user_course.user_id)
    if existing_user_course:
        raise ValueError('User already has that course added.')
    else:
        new_user_course.save()
