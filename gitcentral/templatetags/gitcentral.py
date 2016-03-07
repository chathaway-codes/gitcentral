from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag('gitcentral/_repo_clone.html', takes_context=True)
def render_clone_url(context, repo):
    if 'HTTP_HOST' in context['request'].META:
        hostname = context['request'].META['HTTP_HOST'].split(":")[0]
    else:
        hostname = 'localhost'
    return {'hostname':hostname, 'path': repo.get_relative_path(), 'port': settings.GIT_SERVER_PORT, 'user': context['request'].user}
