from flask_migrate import Migrate, Manager, MigrateCommand

from aggregation import create_app, db
from aggregation import settings
from aggregation.api.modules.accounts.commands import add_user, create_oauth2_client

if __name__ == '__main__':
    app = create_app(settings)
    app.secret_key = settings.SECCRET_KEY
    manager = Manager(app)
    migrate = Migrate(app, db)
    manager.add_command('db', MigrateCommand)
    manager.run()
