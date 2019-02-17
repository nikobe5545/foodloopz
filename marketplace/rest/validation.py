from marketplace import constant
from marketplace.models import User, Organization


class UserAlreadyExistsException(Exception):
    """ Exception thrown if the user already exists """


class PasswordsDoNotMatchExcepion(Exception):
    """ Exception thrown if passwords don't match """


class OrganizationAlreadyExistsException(Exception):
    """ Exception thrown if the organization already exists """


def validate_new_user(user_data: dict):
    email = user_data['email']
    user = User.objects.filter(email=email).first()
    if user:
        raise UserAlreadyExistsException(f'User with email {email} already exists')
    password = user_data[constant.PASSWORD]
    verify_password = user_data[constant.VERIFY_PASSWORD]
    if password != verify_password:
        raise PasswordsDoNotMatchExcepion('Passwords do not match')


def validate_new_organization(organization_data: dict):
    organization_number = organization_data['organizationNumber']
    organization = Organization.objects.filter(organization_number=organization_number).first()
    if organization:
        raise OrganizationAlreadyExistsException(f'Organization with organization number {organization_number} '
                                                 f'already exists')
