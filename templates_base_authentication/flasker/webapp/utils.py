"""Contains common utils for flasker app."""

from flask import Blueprint as BaseBlueprint


class Blueprint(BaseBlueprint):
    """Creates blueprint with method to register class based views."""

    def class_route(self, rule: str, endpoint: str, **options):
        """
        This decorator allows add route to class view.

        :param self: any flask object that have `add_url_rule` method.
        :param rule: flask url rule.
        :param endpoint: endpoint name
        """

        def decorator(cls):
            self.add_url_rule(rule, view_func=cls.as_view(endpoint), **options)
            return cls

        return decorator
