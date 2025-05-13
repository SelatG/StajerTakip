import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
import graphql_jwt
from graphql_jwt.decorators import login_required

from .models import CustomUser, Student, Company, CustomRole, CustomPermission

# === TYPE TANIMLARI === #

class CustomPermissionType(DjangoObjectType):
    class Meta:
        model = CustomPermission
        fields = "__all__"

class CustomRoleType(DjangoObjectType):
    class Meta:
        model = CustomRole
        fields = "__all__"

class UserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = ("id", "email", "role", "is_active","status")

class StudentType(DjangoObjectType):
    class Meta:
        model = Student
        fields = "__all__"

class CompanyType(DjangoObjectType):
    class Meta:
        model = Company
        fields = "__all__"


# === PERMISSION DECORATOR === #

def permission_required(permission_codename):
    def decorator(func):
        def wrapper(root, info, *args, **kwargs):
            user = info.context.user
            if not user.is_authenticated:
                raise GraphQLError("Giriş yapmalısınız.")
            if not user.role.has_permission(permission_codename):
                raise GraphQLError("Bu işlemi yapmaya yetkiniz yok.")
            return func(root, info, *args, **kwargs)
        return wrapper
    return decorator


# === QUERY === #

class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    my_student_profile = graphene.Field(StudentType)
    my_company_profile = graphene.Field(CompanyType)

    all_roles = graphene.List(CustomRoleType)
    all_permissions = graphene.List(CustomPermissionType)

    @login_required
    def resolve_me(self, info):
        return info.context.user

    @login_required
    def resolve_my_student_profile(self, info):
        user = info.context.user
        if hasattr(user, "student_profile"):
            return user.student_profile
        raise GraphQLError("Öğrenci profili bulunamadı.")

    @login_required
    def resolve_my_company_profile(self, info):
        user = info.context.user
        if hasattr(user, "company_profile"):
            return user.company_profile
        raise GraphQLError("Şirket profili bulunamadı.")

    def resolve_all_roles(self, info):
        return CustomRole.objects.all()

    def resolve_all_permissions(self, info):
        return CustomPermission.objects.all()


# === MUTATION === #

class UpdateStudentProfile(graphene.Mutation):
    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        phone = graphene.String()
        address = graphene.String()

    student = graphene.Field(StudentType)

    @login_required
    def mutate(self, info, first_name, last_name, phone=None, address=None):
        user = info.context.user
        if not hasattr(user, "student_profile"):
            raise GraphQLError("Sadece öğrenciler kendi profillerini güncelleyebilir.")

        student = user.student_profile
        student.first_name = first_name
        student.last_name = last_name
        if phone:
            student.phone = phone
        if address:
            student.address = address
        student.save()
        return UpdateStudentProfile(student=student)


# ÖRNEK PERMISSION GEREKTİREN MUTATION
class ApproveCompany(graphene.Mutation):
    class Arguments:
        company_id = graphene.ID(required=True)

    company = graphene.Field(CompanyType)

    @permission_required("approve_company")  # Bu kodename role’a bağlı olmalı
    def mutate(self, info, company_id):
        try:
            company = Company.objects.get(id=company_id)
            # örnek onay mantığı
            # company.is_approved = True
            # company.save()
            return ApproveCompany(company=company)
        except Company.DoesNotExist:
            raise GraphQLError("Şirket bulunamadı.")


# === MUTATION ROOT === #

class Mutation(graphene.ObjectType):
    update_student_profile = UpdateStudentProfile.Field()
    approve_company = ApproveCompany.Field()

    # JWT MUTATIONLARI
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


# === SCHEMA === #

schema = graphene.Schema(query=Query, mutation=Mutation)
