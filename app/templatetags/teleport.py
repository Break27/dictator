from django import template
from django.template.defaulttags import TemplateIfParser
from django.utils.html import format_html

register = template.Library()


class TeleportNode(template.Node):
    context_key = 'teleport_context'

    def __init__(self, nodelist, condition_portals):
        self.nodelist = nodelist
        self.condition_portals = condition_portals
        self.match = None

    @staticmethod
    def get_portals(context):
        return context.render_context.dicts[1].setdefault(
            TeleportNode.context_key, {}
        )

    def evaluate(self, condition, context):
        if condition is not None:
            try:
                self.match = condition.eval(context)
            except template.VariableDoesNotExist:
                self.match = None
        else:
            self.match = True

        return self.match

    def render(self, context):
        for condition, portal_name in self.condition_portals:

            if self.evaluate(condition, context):
                try:
                    portal_name = template.Variable(portal_name).resolve(context)
                except template.VariableDoesNotExist as ex:
                    raise template.VariableDoesNotExist(
                        "Variable '%s' does not exist." % portal_name
                    ) from ex
                portals = self.get_portals(context)
                target = portals.setdefault(portal_name, [])

                if target is None:
                    raise template.TemplateSyntaxError(
                        'Teleport tag must come before portal tag.'
                    )
                target.append(self.nodelist)
                break

        if not self.match:
            output = self.nodelist.render(context)
            return output

        return ''


@register.tag('teleport')
def do_teleport(parser, token):
    """
    Teleport an HTML snippet to the designated portal::

        {% teleport portal_name %}
            <span>Hello world</span>
        {% endteleport %}

    You may provide a variable or an expression before portal_name and a '?' keyword,
    teleport tag will evaluate it just like an if tag::

        {% teleport entries.count > 0 ? 'sidebar' %}
            {% for entry in entries %}
            ...
        {% endteleport %}

    In this case, entries will be teleported to portal 'sidebar' if entries' count
    is greater than 0. If not, this snippet will be rendered normally.

    Moreover, Adding a ':' keyword and another portal name will make this tag to be teleported
    to that portal if the evaluated condition returns a 'falsy' value::

        {% teleport condition ? portal_1 : portal_2 %}
            ...
        {% endteleport %}

    You can provide multiple portal names, along with variables or expressions, separating
    with ':' keywords, to form a chain::

        {% teleport condition_1 ? portal_1 : condition_2 ? portal_2 : ... %}
            ...
        {% endteleport %}

    Teleport tag needs a portal tag to work, and it MUST precede the latter::

        {% portal 'header' %}
        ...
        {% teleport 'header' %} {# This wouldn't work #}
            ...
        {% endteleport %}
    """
    if_sign, endif_sign = '?', ':'

    def split_tokens(separator):
        nonlocal tokens
        result = tokens

        if separator in tokens:
            division = tokens.index(separator)
            if division == 0 or division == len(tokens) - 1:
                raise template.TemplateSyntaxError(
                    "Unexpected keyword '%s'." % separator
                )
            result = tokens[:division]
            tokens = tokens[division + 1:]

        if result == tokens:
            tokens = []

        return result

    tag_name, *tokens = token.split_contents()
    condition_portals = []

    nodelist = parser.parse(('endteleport',))
    parser.delete_first_token()

    if len(tokens) == 0:
        raise template.TemplateSyntaxError(
            '%r tag requires at least one argument.' % tag_name
        )
    elif if_sign in tokens:
        while len(tokens) != 0:
            left_hand = split_tokens(if_sign)
            right_hand = split_tokens(endif_sign)

            if not right_hand:
                raise template.TemplateSyntaxError(
                    "'portal_name' expected."
                )
            if len(right_hand) > 1:
                raise template.TemplateSyntaxError(
                    "'%s [expression]' expected." % endif_sign
                )

            condition = TemplateIfParser(parser, left_hand).parse()
            portal_name = right_hand[0]
            condition_portals.append((condition, portal_name))
    elif len(tokens) > 1:
        raise template.TemplateSyntaxError(
            "'[condition expression] %s portal_name' expected." % if_sign
        )
    else:
        portal_name = tokens[0]
        condition_portals.append((None, portal_name))

    return TeleportNode(nodelist, condition_portals)


@register.simple_tag(name='portal', takes_context=True)
def portal(context, portal_name):
    """
    Create a named portal.

    Portal tag must be after its corresponding teleport tag.
    """
    portals = TeleportNode.get_portals(context)
    this_portal = portals.get(portal_name)
    results = ''

    if this_portal is None:
        portals[portal_name] = None
        return results

    for nodelist in this_portal:
        results += nodelist.render(context)

    return format_html(results)
