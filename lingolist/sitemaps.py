from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticPageSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return [
            "landing",
            "privacy_notice",
            "account_login",
            "account_signup",
            "account_reset_password",
            "use_case_multilingual_shopping_lists",
            "use_case_travel_planning_shared_lists",
            "use_case_roommate_household_task_lists",
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        if item == "landing":
            return 1.0
        if item.startswith("use_case_"):
            return 0.8
        return 0.6

    def changefreq(self, item):
        if item.startswith("use_case_"):
            return "weekly"
        return "monthly"


sitemaps = {"static": StaticPageSitemap}
