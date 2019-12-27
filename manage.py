from flask_migrate import Migrate, Manager, MigrateCommand
from flask_script import Shell

from aggregation import create_app, db
from aggregation import settings
from aggregation.api.commonds.shell import make_context


if __name__ == '__main__':
    app = create_app(settings)
    app.secret_key = settings.SECCRET_KEY
    manager = Manager(app)
    migrate = Migrate(app, db)
    from aggregation.api.modules.transactions.models import Transaction
    manager.add_command('db', MigrateCommand)
    manager.add_command('shell', Shell(make_context=make_context))
    manager.run()
