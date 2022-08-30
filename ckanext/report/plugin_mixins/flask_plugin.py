# encoding: utf-8

import ckan.plugins as p
from ckanext.report import blueprint, cli


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)
    p.implements(p.IClick)

    # IBlueprint

    def get_blueprint(self):
        return blueprint.get_blueprints()

    # IClick

    def get_commands(self):
        return cli.get_commands()
