from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag('gitcentral/_repo_clone.html', takes_context=True)
def render_clone_url(context, repo):
    hostname = context['request'].META['HTTP_HOST'].split(":")[0]
    return {'hostname':hostname, 'path': repo.get_relative_path(), 'port': settings.GIT_SERVER_PORT, 'user': context['request'].user}
