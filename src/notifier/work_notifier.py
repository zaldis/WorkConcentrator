from pynotifier import NotificationClient, Notification
from pynotifier.backends import platform


class WorkNotifier():
    def __init__(self):
        self.notify_client = NotificationClient()
        self.notify_client.register_backend(platform.Backend())

    def send(self, message: str) -> None:
        print('Work Concentrator: ', message)
        notification = Notification(
            title='Work Scheduler',
            message=message,
        )
        self.notify_client.notify_all(notification)
