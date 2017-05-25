from urllib.parse import urljoin
from django.template import Library
from django.template.defaulttags import URLNode, url
from django.conf import settings

register = Library()


class AbsoluteURLNode(URLNode):
    def render(self, context):
        path = super(AbsoluteURLNode, self).render(context)
        domain = settings.BASE_URL
        return urljoin(domain, path)


def absurl(parser, token, node_cls=AbsoluteURLNode):
    """Just like {% url %} but ads the domain of the current site."""
    node_instance = url(parser, token)
    return node_cls(view_name=node_instance.view_name,
                    args=node_instance.args,
                    kwargs=node_instance.kwargs,
                    asvar=node_instance.asvar)

absurl = register.tag(absurl)
