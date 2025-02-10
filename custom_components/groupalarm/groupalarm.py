import requests

GROUP_ALARM_BASE_URL = "https://app.groupalarm.com/api/v1"

class GroupAlarm:
    def __init__(self, api_key: str, organization_id: int, test=True):
        """
            :param api_key: GroupAlarm API key (Bearer token)
            :param organization_id: Organization ID (integer) from GroupAlarm, used in API path
        :param test: If True, send out a preview alarm to test the connection and permissions
        :raises ValueError: If test==True and the api_key and organization_id combination doesn't allow sending alarms
        """
        self._api_key = api_key
        self._organization_id = organization_id

        if test:
            test_result = self.send_groupalarm_alarm(message="test", preview=True)
            if not test_result["success"]:
                raise ValueError(
                    f"Test failed with status code {test_result["status_code"]} and message {test_result['message']}")

    def send_groupalarm_alarm(self,
                              message: str,
                              category: str = None,
                              target_group: str = None,
                              event_name: str = "alarm",
                              alarm_resources: dict = {"allUsers": True, },
                              timeout: int = 10,
                              preview: bool = False,
                              ):
        """
        Send an alarm through GroupAlarm's API.

            :param message: Alarm message content (required)
            :param category: Alarm category (e.g., 'fire', 'security'). Optional but recommended.
            :param target_group: Target group ID. Optional but either target_group or alarm_resources must be specified.
            :param event_name: Type of alarm event (default: "alarm")
            :param alarm_resources: Dictionary specifying alarm targets, defaults to {"allUsers": True}.
                             Example: {"allUsers": False, "resources": ["device_123", "device_456"]}
            :param timeout: Request timeout in seconds (default: 10)

        :returns            Dictionary containing:
            - success: Boolean indicating success
            - status_code: HTTP status code
            - data: Response data (dict) or error message (str)
        """
        url = f"{GROUP_ALARM_BASE_URL}/alarm"
        if preview:
            url += "/preview"
        headers = {
            "API-TOKEN": self._api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "organizationID": self._organization_id,
            "message": message,
            "alarmResources": alarm_resources,
            "eventName": event_name,
        }
        if category:
            payload["category"] = category
        if target_group:
            payload["targetGroup"] = target_group

        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        try:
            response.raise_for_status()
            response_data = response.json()

            return {
                "success": True,
                "status_code": response.status_code,
                "data": response_data
            }

        except requests.exceptions.RequestException as err:
            status_code = response.status_code
            return {
                "success": False,
                "status_code": status_code,
                "data": response.text
            }

        except (requests.exceptions.ConnectionError, TimeoutError) as err:
            return {
                "success": False,
                "status_code": None,
                "data": f"Request failed: {str(err)}"
            }


def _test():
    # TODO replace api key and organization ID
    API_KEY = '<<your_api_key>>'
    organization_id = 123456
    ga = GroupAlarm(API_KEY, organization_id)
    alarm_result = ga.send_groupalarm_alarm("Hallo :D", preview=True)
    print(alarm_result)


if __name__ == '__main__':
    _test()
    # asyncio.run(_test())
