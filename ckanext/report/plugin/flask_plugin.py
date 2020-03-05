# -*- coding: utf-8 -*-

import ckan.plugins as p
import ckanext.report.blueprint as views

class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBluePrint)

    # IBlueprint

    def get_blueprint(self):
        return views.get_blueprints()