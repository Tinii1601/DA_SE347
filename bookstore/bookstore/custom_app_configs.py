from django.contrib.auth.apps import AuthConfig
from django.contrib.sites.apps import SitesConfig
from allauth.account.apps import AccountConfig
from allauth.socialaccount.apps import SocialAccountConfig


class CustomAuthConfig(AuthConfig):
    verbose_name = "Xác thực và ủy quyền"


class CustomSitesConfig(SitesConfig):
    verbose_name = "Các trang web"


class CustomAccountConfig(AccountConfig):
    verbose_name = "Tài khoản"


class CustomSocialAccountConfig(SocialAccountConfig):
    verbose_name = "Mạng xã hội"
