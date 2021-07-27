from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Sum
from .models import *
from .forms import *
from .helpers import save_user_course
from .helpers import Semester
import datetime
# Create your views here.

# def main_dash(request):
#
#     schools = School.objects.filter(userpath__user=request.user).distinct()
#     school_majors = SchoolMajor.objects.filter(userpath__user=request.user).distinct()
#     school_major_form = SelectMajorForm(request=request)
#     school_major_form.fields['school_majors'].queryset = school_majors
#     major_requirements = MajorRequirement.objects.filter(school_major__in=school_majors)
#
#     if request.method == 'POST':
#         form = SelectMajorForm(request.POST)
#         if form.is_valid():
#             chosen_major = form.cleaned_data['school_majors']
#             major_requirements = MajorRequirement.objects.filter(school_major__in=chosen_major)
#
#
#     return render(request, 'app/main_dash.html',
#                     {'user': request.user,
#                     'schools': schools,
#                     'school_majors':school_majors,
#                     'major_requirements':major_requirements,
#                     'form': school_major_form
#                     })

# def path_detail(request, id):
#     chosen_major = SchoolMajor.objects.get(id=id)
#     schools = School.objects.filter(userpath__user=request.user).distinct()
#     school_majors = SchoolMajor.objects.filter(userpath__user=request.user).distinct()
#     major_requirements = MajorRequirement.objects.filter(school_major=chosen_major)
#     school_major_form = SelectMajorForm(request=request)
#     school_major_form.fields['school_majors'].queryset = school_majors
#     major_courses = SchoolCourse.objects.filter(majorrequirementcourse__major_requirement__in=major_requirements)
#     # major_courses = MajorRequirementCourse.objects.filter(major_requirement__in = major_requirements)
#     # Get the user courses that match the user_id and that fall under the selected major
#     # user_courses = UserCourse.objects.filter(user=request.user).filter(school_course__in=major_courses)
#     user_courses = UserCourse.objects.raw('''SELECT
#                                             	a.*
#                                             	, c.req_number
#                                             	, c.description
#                                             FROM app_usercourse a
#                                             join app_majorrequirementcourse b on a.school_course_id = b.school_course_id
#                                             join app_majorrequirement c on b.major_requirement_id = c.id
#                                             WHERE a.user_id = %s
#                                             AND c.school_major_id = %s'''
#                                             , [request.user.id, chosen_major.id])
#
#     d = {}
#     for uc in user_courses:
#         mr = uc.school_course.majorrequirementcourse_set.filter(major_requirement__in = major_requirements)
#         d[uc.id] = mr
#
#     if request.method == 'POST':
#         form = SelectMajorForm(request.POST)
#         if form.is_valid():
#             chosen_major = form.cleaned_data['school_majors']
#             url = reverse('path_detail', kwargs={'id': chosen_major.id})
#             return HttpResponseRedirect(url)
#
#     return render(request, 'app/path_detail.html',
#                     {'user': request.user,
#                     'schools': schools,
#                     'school_majors':school_majors,
#                     'form': school_major_form,
#                     'major_requirements':major_requirements,
#                     'method': request.method,
#                     'chosen_major': chosen_major,
#                     'user_courses': user_courses,
#                     'mr': d
#                     })

def path_overview(request):

    schools = School.objects.filter(userpath__user=request.user).distinct()
    school_majors = SchoolMajor.objects.filter(userpath__user=request.user).distinct()
    school_major_form = SelectMajorForm(request=request)
    school_major_form.fields['school_majors'].queryset = school_majors

    user_path_form = AddUserPath()

    if request.method == 'POST':

        if 'major_submission' in request.POST:
            form = SelectMajorForm(request.POST)
            if form.is_valid():
                chosen_major = form.cleaned_data['school_majors']
                url = reverse('path_detail', kwargs={'id': chosen_major.id})
                return HttpResponseRedirect(url)

        if 'addpath_submission' in request.POST:
            add_user_path_form = AddUserPath(request.POST)
            if add_user_path_form.is_valid():
                userpath = add_user_path_form.save(commit=False)
                userpath.user = request.user
                userpath.school = schools.get()
                if UserPath.objects.filter(user = request.user).filter(school_major=userpath.school_major).count() > 0:
                    return redirect('path_overview')
                else:
                    userpath.save()
                return redirect('path_overview')

    return render(request, 'app/path_overview.html',
                    {'user': request.user,
                    'schools': schools,
                    'school_majors':school_majors,
                    'form': school_major_form,
                    'user_path_form':user_path_form,
                    'method': request.method
                    })

# AJAX
def load_schoolmajors(request):
    school_id = request.GET.get('school_id')
    schoolmajors = SchoolMajor.objects.filter(school_id=school_id).all()
    return render(request, 'app/schoolmajor_dropdown_list_options.html', {'schoolmajors': schoolmajors})


def path_detail(request, id):
    chosen_major = SchoolMajor.objects.get(id=id)
    schools = School.objects.filter(userpath__user=request.user).distinct()
    school_majors = SchoolMajor.objects.filter(userpath__user=request.user).distinct()
    major_requirements_orig = MajorRequirement.objects.filter(school_major=chosen_major)
    user_path = UserPath.objects.filter(user=request.user).filter(school_major=chosen_major).get()

    term_semester_choices = [s.value for s in Semester]
    year = datetime.datetime.today().year
    term_year_choices = list(range(year, year + 3, 1))
    major_requirement_query = ''' with stage as (
                        SELECT
                        	a.id
                        	, a.req_number
                        	, a.description
                        	, a.guidance
                        	, b.fulfillment_option
							, e.fulfillment_option as preferred_fulfillment_option
                        	, total_components
                        	, cast(COUNT(CASE WHEN d.status = 'CO' THEN d.school_course_id END) as float)/min(total_components) as completion
                            , ARRAY_AGG(b.school_course_id) as course_id
                            , ARRAY_AGG(CONCAT(c.department,' ', CAST(c.number as varchar))) as course
                        	, ARRAY_AGG(CASE WHEN d.school_course_id is not null then CONCAT(c.department,' ', CAST(c.number as varchar)) END) as user_course
                            , ARRAY_AGG(CASE WHEN d.school_course_id is not null then CONCAT(d.semester,' ', d.year) END) as user_course_term
                            , ARRAY_AGG(CASE WHEN d.school_course_id is not null then d.status END) as user_course_status
                        from app_majorrequirement a
						JOIN app_userpath up on a.school_major_id = up.school_major_id and up.user_id = %s and up.school_major_id = %s
                        LEFT JOIN app_majorrequirementcourse b on a.id = b.major_requirement_id
                        LEFT JOIN app_schoolcourse c on b.school_course_id = c.id
                        LEFT JOIN app_usercourse d on b.school_course_id = d.school_course_id
						LEFT JOIN app_userpathpreference e on a.id = e.major_requirement_id
                        WHERE (b.major_requirement_id is null OR c.school_id = %s)
                        GROUP BY 1,2,3,4,5,6,7
                        order by 2,5
                        )
                        select
                        	id
                        	, req_number
                        	, description
                        	, guidance
							, preferred_fulfillment_option
                        	, count(fulfillment_option) as fullfillment_options
                        	, array_agg(total_components) as total_components
                        	, json_agg(completion) as completion
                        	, json_agg(course) as course
                            , json_agg(course_id) as course_id
                        	, json_agg(user_course) as user_course
                            , json_agg(user_course_term) as user_course_term
                            , json_agg(user_course_status) as user_course_status
                        from stage
                        group by 1,2,3,4,5
                        order by 1,2
                        '''
    major_requirements = MajorRequirement.objects.raw(major_requirement_query, [request.user.id, chosen_major.id, schools.get().id])
        # print(len([i.completion for i in major_requirements]))
    # print(len([i.completion for i in major_requirements if i.fullfillment_options > 0 ]))
    # print(sum([i.completion[i.preferred_fulfillment_option] for i in major_requirements if i.preferred_fulfillment_option is not None]))
    # print(sum([i.completion[0] for i in major_requirements if i.fullfillment_options==1]))

    school_major_form = SelectMajorForm(request=request)
    school_major_form.fields['school_majors'].queryset = school_majors

    selected_option = ''
    if request.method == 'POST':
        print(request.POST)
        if 'select_goal' in request.POST:
            form = SelectMajorForm(request.POST)
            if form.is_valid():
                chosen_major = form.cleaned_data['school_majors']
                url = reverse('path_detail', kwargs={'id': chosen_major.id})
                return HttpResponseRedirect(url)
        if 'select_option' in request.POST and request.POST.get("fulfillmentoption") !='':
            selected_option = request.POST.get("fulfillmentoption")
            req_num, option_num = selected_option.split('.')

            major_req = major_requirements_orig.filter(req_number=int(req_num)).get()
            UserPathPreference.objects.update_or_create(user_path=user_path,
                                                major_requirement=major_req,
                                                defaults={'fulfillment_option': option_num})

        if 'select_term_option' in request.POST and request.POST.get("termoption") !='':
            selected_term_option = request.POST.get("termoption")
            semester, year, course_id = selected_term_option.split(' ')
            UserCourse.objects.update_or_create(school_course_id=course_id,
                                                user_id=request.user.id,
                                                defaults={'semester': semester, 'year': year})

        if 'add_to_schedule' in request.POST:
            print("hemwmer")

        major_requirements = MajorRequirement.objects.raw(major_requirement_query, [request.user.id, chosen_major.id, schools.get().id])
    num_of_major_requirements = len([i.completion for i in major_requirements])
    num_of_major_requirements_with_articulation = len([i.completion for i in major_requirements if i.fullfillment_options > 0 ])
    num_of_major_requirements_completed = sum([i.completion[i.preferred_fulfillment_option] for i in major_requirements if i.preferred_fulfillment_option is not None])+sum([i.completion[0] for i in major_requirements if i.fullfillment_options==1])


    return render(request, 'app/path_detail.html',
                    {'user': request.user,
                    'schools': schools,
                    'school_majors':school_majors,
                    'form': school_major_form,
                    'major_requirements':major_requirements,
                    'method': request.method,
                    'chosen_major': chosen_major,
                    'term_year_choices':term_year_choices,
                    'term_semester_choices': term_semester_choices,
                    'num_of_major_requirements':num_of_major_requirements,
                    'num_of_major_requirements_with_articulation':num_of_major_requirements_with_articulation,
                    'num_of_major_requirements_completed':num_of_major_requirements_completed
                    })


def add_course(request, course_id):
    course_schedule = CourseSchedule.objects.filter(school_course_id=course_id)
    display_msg = "meemow"

    if request.method == 'POST':
        display_msg = "FOICK YA"
        if 'course' in request.POST:
            course_schedule_id = request.POST.get('course')
            try:
                save_user_course(course_schedule_id, request.user.id)
                display_msg = 'FOICK YA U ADDED DAT CLASS'
            except ValueError as error:
                display_msg = error

    return render(request, 'app/add_course.html',
                    {'course_id': course_id,
                    'course_schedule': course_schedule,
                    'display_msg': display_msg
                    })
