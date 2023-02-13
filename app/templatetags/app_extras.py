from django import template

register = template.Library()


class OnceNode(template.Node):
    context_key = 'once_context'

    def __init__(self, nodelist, name):
        self.nodelist = nodelist
        self.name = name

    def render(self, context):
        rendered = context.render_context.dicts[1].setdefault(
            self.context_key, set()
        )
        snippet = context.render_context.template.name

        if self.name is not None:
            snippet = '%s@%s' % (self.name, snippet)

        if snippet not in rendered:
            rendered.add(snippet)
            return self.nodelist.render(context)

        return ''


@register.tag('once')
def do_once(parser, token):
    """
    Mark a snippet to be rendered only once.

    A name is required for distinguishing multiple once tags in a single HTML file.
    """
    try:
        _, name = token.split_contents()
    except ValueError:
        name = None

    nodelist = parser.parse(('endonce',))
    parser.delete_first_token()

    return OnceNode(nodelist, name)

