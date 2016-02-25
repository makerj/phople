from django.apps import AppConfig
from apiserver.util import aws
import os


class APIServerAppConfig(AppConfig):
    name = 'apiserver'
    verbose_name = "RESTful phople api server"

    def ready(self):
        info = '[PID {pid}]initiating apiserver... [{ok}]'
        print(info.format(pid=os.getpid(), ok='PENDING'))
        aws.init()
        print(info.format(pid=os.getpid(), ok='OK'))
