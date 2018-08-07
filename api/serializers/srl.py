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


class TeacherSer(serializers.ModelSerializer):

    class Meta:
        model = Teacher
        fields = '__all__'


class ScholarshipSer(serializers.ModelSerializer):

    class Meta:
        model = Scholarship
        fields = '__all__'


class OftenAskedQuestionSer(serializers.ModelSerializer):

    class Meta:
        model = OftenAskedQuestion
        fields = '__all__'


class CourseChapterSer(serializers.ModelSerializer):

    class Meta:
        model = CourseChapter
        fields = '__all__'


class CourseSectionSer(serializers.ModelSerializer):

    class Meta:
        model = CourseSection
        fields = '__all__'
