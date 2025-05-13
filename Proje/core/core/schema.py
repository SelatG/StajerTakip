import graphene

from users.schema import Query as UsersQuery
from users.schema import Mutation as UsersMutation

from internships.schema import Query as InternshipQuery
from internships.schema import Mutation as InternshipMutation


# === Birleşik Query ve Mutation === #

class Query(UsersQuery, InternshipQuery, graphene.ObjectType):
    pass

class Mutation(UsersMutation, InternshipMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
