from rest_framework import serializers
from rest_framework.validators import ValidationError
from api.models import CourseCategory, CourseSubCategory, DegreeCourse, Teacher, Scholarship, Course, CourseDetail, OftenAskedQuestion, CourseOutline, CourseChapter, CourseSection, Homework, PricePolicy


class CourseSer(serializers.ModelSerializer):
    level = serializers.CharField(
        source='get_level_choices_display', read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
        # depth = 1


class DegreeCourseSer(serializers.ModelSerializer):

    class Meta:
        model = DegreeCourse
        fields = '__all__'
        # fields = ['name', 'total_scholarship', ]
