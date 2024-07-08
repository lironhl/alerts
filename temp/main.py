import logging
import os
from typing import Optional

import requests

HIGH_TEMP = 60
CRITICAL_TEMP = 80

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# At First we have to get the current CPU-Temperature with this defined function
def get_cpu_temp() -> float:
    res = os.popen("vcgencmd measure_temp").readline()
    formatted_res = res.replace("temp=", "").replace("'C\n", "")

    logger.debug("cpu temp - {res}".format(res=formatted_res))

    return 40


def get_urgency_and_message(temp: float) -> tuple[bool, Optional[str]]:
    if temp > CRITICAL_TEMP:
        return (
            True,
            "Critical warning! The actual temperature is: {} \n\n Shutting down the pi!".format(
                temp
            ),
        )
    elif temp > HIGH_TEMP:
        return False, "Warning! The actual temperature is: {} ".format(temp)
    return False, None


def send_message(message: str):
    requests.post("https://ntfy.sh/lironhlpi", data=message.encode(encoding="utf-8"))


def main():
    logger.info("starting alert")

    temp = get_cpu_temp()
    is_critical, message = get_urgency_and_message(temp)

    if message is not None:
        logger.info("sending message")
        send_message(message)

    if is_critical:
        logger.info("halting the system")
        os.popen("sudo halt")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("alert failed")