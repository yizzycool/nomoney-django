from works.models import User, Case, Application, Hashtag, MiddleAgent


# Function
def get_crud_profile(obj):
    return {
        'noData': False,
        'userId': obj.userId,
        'displayName': obj.displayName,
        'image': obj.image,
        'intro': obj.intro,
        'gender': obj.gender,
        'birthday': obj.birthday,
        'phone': obj.phone,
        'county': obj.county,
        'rating': obj.rating,
        'lineId': obj.lineId,
    }



# Function
def get_crud_case(obj):
    return {
        'noData': False,
        'employerId': obj.employerId.userId,
        'title': obj.title,
        'text': obj.text,
        'location': obj.location,
        'pay': obj.pay,
        'status': obj.status,
        'publishTime': obj.publishTime,
        'modifiedTime': obj.modifiedTime,
        'caseId': obj.id,
        'hashtag': [ 
            mid_obj.hashtag.tag for mid_obj in obj.middleagent_set.all()
        ]
    }



# Function
def get_crud_application(obj):
    return {
        'noData': False,
        'caseId': obj.caseId.id,
        'employeeId': obj.employeeId.userId,
        'message': obj.message,
        'accepted': obj.accepted,
        'employerRating': obj.employerRating,
        'employeeRating': obj.employeeRating,
    }


