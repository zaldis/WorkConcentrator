import os.path
from os.path import join

from pynotifier import NotificationClient, Notification
from pynotifier.backends import platform


class WorkNotifier():
    def __init__(self):
        self.notify_client = NotificationClient()
        self.notify_client.register_backend(platform.Backend())

    def send(self, message: str) -> None:
        print('Work Concentrator: ', message)
        icon_path = os.path.abspath(join('.', 'media', 'icon.ico'))
        print(icon_path)
        notification = Notification(
            title='Work Scheduler',
            message=message,
            icon_path=icon_path,
        )
        self.notify_client.notify_all(notification)
