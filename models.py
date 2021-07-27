from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class School(models.Model):
    name = models.CharField(max_length=100)
    year_type = models.SmallIntegerField()
    college_type = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=5)

    def __str__(self):
        return self.name


class SchoolMajor(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    degree_type = models.CharField(max_length=20)

    def __str__(self):
        return self.degree_type + " in " + self.name + " at " + self.school.name


class SchoolCourse(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    units = models.SmallIntegerField(null=True)

    def __str__(self):
        return self.department + " " + self.number


class MajorRequirement(models.Model):
    school_major = models.ForeignKey(SchoolMajor, on_delete=models.CASCADE)
    req_number = models.SmallIntegerField()
    guidance = models.CharField(max_length=200)
    description = models.CharField(max_length=200)


class MajorRequirementCourse(models.Model):
    major_requirement = models.ForeignKey(MajorRequirement, on_delete=models.CASCADE)
    school_course = models.ForeignKey(SchoolCourse, on_delete=models.CASCADE)
    component_number = models.SmallIntegerField()
    total_components = models.SmallIntegerField()
    fulfillment_option = models.SmallIntegerField()

class GeneralEdRequirement(models.Model):
    ge_type = models.CharField(max_length=10)
    area_level_1 = models.CharField(max_length=100)
    area_level_2 = models.CharField(max_length=100)
    college_type = models.CharField(max_length=10)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)


class GeneralEdRequirementCourse(models.Model):
    general_ed_requirement = models.ForeignKey(GeneralEdRequirement, on_delete=models.CASCADE)
    school_course = models.ForeignKey(SchoolCourse, on_delete=models.CASCADE)


class UserPath(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    school_major = models.ForeignKey(SchoolMajor, on_delete=models.CASCADE)


class UserPathPreference(models.Model):
    user_path = models.ForeignKey(UserPath, on_delete=models.CASCADE)
    major_requirement = models.ForeignKey(MajorRequirement, on_delete=models.CASCADE)
    fulfillment_option = models.SmallIntegerField()


class UserCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    school_course = models.ForeignKey(SchoolCourse, on_delete=models.CASCADE)
    semester = models.CharField(max_length=4)
    year = models.CharField(max_length=4)
    status = models.CharField(max_length=10)
    grade = models.CharField(max_length=5, null=True, blank=True)

    def __str__(self):
        return school_course.department + " " + school_course.number


class CourseSchedule(models.Model):
    starts_at = models.DateField()
    ends_at = models.DateField()
    term = models.CharField(max_length=15)
    meeting_times = models.JSONField(blank=True, default=dict)
    class_type = models.CharField(max_length=50)
    course_reference_number = models.CharField(max_length=10)
    component_name = models.CharField(max_length=30)
    component_level = models.SmallIntegerField()
    instructor = models.CharField(max_length=50)
    location = models.CharField(max_length=100, blank=True, default='')
    prerequisites = models.CharField(max_length=200, blank=True, default='')
    class_size = models.SmallIntegerField()
    waitlist_size = models.SmallIntegerField()
    enrolled_count = models.SmallIntegerField()
    waitlisted_count = models.SmallIntegerField()
    school_course = models.ForeignKey(SchoolCourse, on_delete=models.CASCADE)

    @property
    def school_course_crn(self):
        return "%s_%s" % (self.school_course.id, self.course_reference_number)

class CourseRelationships(models.Model):
    parent_course_schedule = models.ForeignKey(CourseSchedule, related_name='parent_course_schedule', on_delete=models.CASCADE)
    child_course_schedule = models.ForeignKey(CourseSchedule, related_name='child_course_schedule', on_delete=models.CASCADE)

class UserCourseSchedule(models.Model):
    status = models.CharField(max_length=30)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    course_schedule = models.ForeignKey(CourseSchedule, on_delete=models.CASCADE)
