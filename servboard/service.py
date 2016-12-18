import socket
import os
import json

from tornado.web import RequestHandler
from tornado.gen import coroutine
import psutil
import humanize
import click

from pymicroservice.core.microservice import PyMicroService
from pymicroservice.core.decorators import public_method, private_api_method

from servboard import __version__


# example custom request handler
class IndexHandler(RequestHandler):
    @coroutine
    def get(self):
        node_name = socket.gethostname()
        cpu_times = psutil.cpu_percent(percpu=True)
        memory_stat = psutil.virtual_memory()

        disks = psutil.disk_partitions()
        disk_status = {}
        for disk in disks:
            try:
                disk_status[disk.mountpoint] = psutil.disk_usage(disk.mountpoint)
            except OSError:
                disk_status[disk.mountpoint] = None

        try:
            with open(".services") as f:
                services = json.load(f)
        except FileNotFoundError:
            services = {}

        self.render("index.html", version=__version__, node_name=node_name, cpu_times=cpu_times,
                    memory_total_raw=memory_stat.total, memory_used_raw=memory_stat.used,
                    memory_total_humanized=humanize.naturalsize(memory_stat.total),
                    memory_used_humanized=humanize.naturalsize(memory_stat.used),
                    disk_status=disk_status, services=services,

                    # misc
                    naturalsize=humanize.naturalsize
                    )


class ServboardService(PyMicroService):
    name = "servboard"
    host = "0.0.0.0"
    port = 80

    api_token_header = "X-Api-Token"
    max_parallel_blocking_tasks = os.cpu_count()

    extra_handlers = [
        (r"/", IndexHandler),
    ]

    # create your templates
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "html", "templates")

    # setup your static files
    static_dirs = [
        (r"/static", os.path.join(os.path.dirname(os.path.abspath(__file__)), "html", "static")),
    ]

    def on_service_start(self):
        with open(".services", "w") as f:
            f.write(json.dumps(self.services))

    def __init__(self, services):
        """
        Services must be a dict with the key == service name and value == service location

        :param services:
        """
        self.services = services
        super(ServboardService, self).__init__()


@click.command()
@click.option("--services_file", help="A JSON file from where to extract the services")
def main(services_file=None):
    if services_file:
        with open(services_file) as svc_file:
            data = json.load(svc_file)
    else:
        data = {}
    service = ServboardService(data)
    service.start()
