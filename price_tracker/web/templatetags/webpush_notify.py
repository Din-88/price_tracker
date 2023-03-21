from django import template
from django.conf import settings
from django.urls import reverse

register = template.Library()

# @register.simple_tag
# def webpush_header():
#     return {'data': 'test_data'}


@register.filter
@register.inclusion_tag('webpush/webpush_head.html', takes_context=True)
def webpush_head(context):
    request = context['request']
    vapid_public_key = getattr(settings, 'WEBPUSH_SETTINGS', {}).get('VAPID_PUBLIC_KEY', '')

    data = {'group': context.get('webpush', {}).get('group'),
        'user': getattr(request, 'user', None),
        'vapid_public_key': vapid_public_key,
        'webpush_save_url': reverse('save_webpush_info')
    }

    template_context = data
    return template_context