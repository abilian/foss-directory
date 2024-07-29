import click
from flask.cli import with_appcontext

from .job import Job


#
# Other operational commands
#
@click.command()
@click.argument("args", nargs=-1)
@with_appcontext
def job(args):
    if not args:
        print("Usage: 'flask job <job_name> <args> where:")
        for job_class in Job.registry:
            print(f"{job_class.name}: {job_class.description}")
        return

    job_name = args[0]
    for job_class in Job.registry:
        if job_class.name == job_name:
            job = job_class(*args[1:])
            job.run()
            return

    print(f"No such job: {job_name}")
