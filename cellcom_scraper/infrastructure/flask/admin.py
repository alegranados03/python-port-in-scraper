from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from cellcom_scraper.infrastructure.flask.model_views import (
    AccountModelView,
    NavigatorModelView,
    ScraperModelView,
    ScraperRequestExtrasModelView,
    ScraperRequestModelView,
)
from cellcom_scraper.infrastructure.sqlalchemy.database import SESSION_FACTORY
from cellcom_scraper.infrastructure.sqlalchemy.models import (
    Account,
    Navigator,
    Scraper,
    ScraperRequest,
    ScraperRequestExtras,
)


def init_admin(app):
    session = SESSION_FACTORY()
    admin = Admin(app, name="Scraper Administration", template_mode="bootstrap4")
    # admin.add_view(ModelView(Scraper, session))
    # admin.add_view(ModelView(Account, session))
    # admin.add_view(ModelView(Navigator, session))
    # admin.add_view(ScraperRequestExtrasModelView(ScraperRequestExtras, session))
    # admin.add_view(ScraperRequestModelView(ScraperRequest, session))

    admin.add_view(AccountModelView(Account, session))
    admin.add_view(ScraperRequestModelView(ScraperRequest, session))
    admin.add_view(NavigatorModelView(Navigator, session))
    admin.add_view(ScraperModelView(Scraper, session))
