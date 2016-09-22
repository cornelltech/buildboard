import re

from django.contrib.auth import logout

from accounts.models import Account
from django.shortcuts import redirect

# ref: http://stackoverflow.com/questions/13018147/authalreadyassociated-exception-in-django-social-auth
def social_user(backend, uid, user=None, *args, **kwargs):
    '''OVERRIDED: It will logout the current user
    instead of raise an exception '''

    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)
    if social:
        if user and social.user != user:
            logout(backend.strategy.request)
            #msg = 'This {0} account is already in use.'.format(provider)
            #raise AuthAlreadyAssociated(backend, msg)
        elif not user:
            user = social.user
    return {'social': social,
            'user': user,
            'is_new': user is None,
            'new_association': False}


def validate_cornell_email(backend, details, response, *args, **kwargs):
    cornell_email_pattern = re.compile("^([A-Za-z0-9._%+-])+@cornell.edu$")
    new_school_email_pattern = re.compile("^([A-Za-z0-9._%+-])+@newschool.edu$")
    if cornell_email_pattern.match(details.get('email')) is None
            and new_school_email_pattern.match(details.get('email')) is None:
        return redirect('accounts:login')


def get_avatar(backend, strategy, details, response, user=None, *args, **kwargs):
    url = None
    if backend.name == 'facebook':
        url = "http://graph.facebook.com/%s/picture?type=large"%response['id']
    if backend.name == 'twitter':
        url = response.get('profile_image_url', '').replace('_normal','')
    if backend.name == 'google-oauth2':
        url = response['image'].get('url')
        ext = url.split('.')[-1]

    if url:
        try:
            if user.account:
                user.account.avatar = url
                user.account.save()
            else:
                Account.objects.create(user=user, avatar=url)
        except Account.DoesNotExist:
            Account.objects.create(user=user, avatar=url)