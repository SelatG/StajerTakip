import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from .models import Internship, InternshipDiary, Evaluation
from users.models import CustomUser


# === TYPE TANIMLARI === #

class InternshipType(DjangoObjectType):
    class Meta:
        model = Internship
        fields = "__all__"


class InternshipDiaryType(DjangoObjectType):
    class Meta:
        model = InternshipDiary
        fields = "__all__"


class EvaluationType(DjangoObjectType):
    class Meta:
        model = Evaluation
        fields = "__all__"


# === QUERY === #

class Query(graphene.ObjectType):
    my_internships = graphene.List(InternshipType)
    internship_diaries = graphene.List(InternshipDiaryType, internship_id=graphene.ID(required=True))
    internship_evaluations = graphene.List(EvaluationType, internship_id=graphene.ID(required=True))

    @login_required
    def resolve_my_internships(self, info):
        user = info.context.user
        return Internship.objects.filter(student=user) | Internship.objects.filter(company=user)

    @login_required
    def resolve_internship_diaries(self, info, internship_id):
        return InternshipDiary.objects.filter(internship_id=internship_id)

    @login_required
    def resolve_internship_evaluations(self, info, internship_id):
        return Evaluation.objects.filter(internship_id=internship_id)


# === MUTATION === #

class CreateInternship(graphene.Mutation):
    class Arguments:
        company_id = graphene.ID(required=True)
        topic = graphene.String(required=True)
        description = graphene.String()
        start_date = graphene.types.datetime.Date(required=True)
        end_date = graphene.types.datetime.Date(required=True)

    internship = graphene.Field(InternshipType)

    @login_required
    def mutate(self, info, company_id, topic, description=None, start_date=None, end_date=None):
        student = info.context.user
        try:
            company = CustomUser.objects.get(id=company_id)
        except CustomUser.DoesNotExist:
            raise GraphQLError("Şirket bulunamadı.")

        internship = Internship.objects.create(
            student=student,
            company=company,
            topic=topic,
            description=description,
            start_date=start_date,
            end_date=end_date,
        )
        return CreateInternship(internship=internship)


class CreateInternshipDiary(graphene.Mutation):
    class Arguments:
        internship_id = graphene.ID(required=True)
        day_number = graphene.Int(required=True)
        content = graphene.String(required=True)
        date = graphene.types.datetime.Date(required=True)

    diary = graphene.Field(InternshipDiaryType)

    @login_required
    def mutate(self, info, internship_id, day_number, content, date):
        user = info.context.user
        internship = Internship.objects.get(id=internship_id)

        if internship.student != user:
            raise GraphQLError("Yalnızca kendi staj günlüğünüzü oluşturabilirsiniz.")

        diary = InternshipDiary.objects.create(
            internship=internship,
            day_number=day_number,
            content=content,
            date=date,
        )
        return CreateInternshipDiary(diary=diary)


class Mutation(graphene.ObjectType):
    create_internship = CreateInternship.Field()
    create_internship_diary = CreateInternshipDiary.Field()


# === SCHEMA === #

internship_schema = graphene.Schema(query=Query, mutation=Mutation)
