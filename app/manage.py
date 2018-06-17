import click
from datetime import datetime
from validate_email import validate_email
from app import app, db
from app.models import User


def clear_data(session):
    """
    Clear data from the database
    """
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        click.echo(f'Clear table {table}')
        session.execute(table.delete())

    session.commit()
    click.echo('Done!')


@app.cli.command()
def clear_db():
    clear_data(db.session)


@app.cli.command()
def drop_db():
    db.reflect()
    db.drop_all()
    click.echo('The database was droped!')


@app.cli.command()
def init_db():
    db.create_all()
    click.echo('The database was created!')


@app.cli.command('createsuperuser')
@click.argument('superuser', nargs=3)
def create_user(superuser):
    username, email, password = superuser[0], superuser[1], superuser[2]
    check_user = User.query.filter_by(username=username).first() or \
        User.query.filter_by(email=email).first()

    if check_user:
        click.echo(f'This user has been already created! Username: {username} Email: {email}.')
        return

    email_is_valid = validate_email(email)
    if not email_is_valid:
        click.echo('Please enter a valid email address!')
        return

    user = User(
        username=username,
        email=email,
        password=password,
        full_name='Test Name',
        confirmed=True,
        confirmed_on=datetime.now(),
        superuser=True
        )
    db.session.add(user)
    db.session.commit()
    click.echo('The user was successfuly created!')
