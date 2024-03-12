import requests
from libqtile.widget import base
from libqtile.log_utils import logger

class GithubNotifications(base.ThreadPoolText):
    """
    A Qtile widget to display the number of unread notifications from GitHub.
    """
    orientations = base.ORIENTATION_HORIZONTAL

    defaults = [
        ("access_token", None, "Github access token"),
        ("format", "{unread}", "Status message format"),
        ("no_unread_format", "", "Status message format")
    ]

    def __init__(self, *args, **kwargs):
        base.ThreadPoolText.__init__(self, "", *args, **kwargs)
        self.add_defaults(GithubNotifications.defaults)

    def _get_values(self):
        result = dict()
        try:
            response = requests.get(
                url = "https://api.github.com/notifications",
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "X-GitHub-Api-Version": "2022-11-28"
                }
            )
            if response.status_code != 200:
                result["error"] = f"Unexpected status code:{response.status_code}"
                return result

            notifications = response.json()
            result["unread"] = len(notifications)
            result["error"] = None
            return result
        except Exception as e:
            result["error"]=e
            return result

    def poll(self):
        notification_info = self._get_values()

        if notification_info["error"] is not None:
            logger.error(f"GithubNotification error: {notification_info['error']}")
            return f"Error: {notification_info['error']}"
        
        if notification_info["unread"] == 0:
            return self.no_unread_format.format(**notification_info)
        
        return self.format.format(**notification_info)
