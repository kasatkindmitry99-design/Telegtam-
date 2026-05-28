import time

user_last_message = {}

COOLDOWN = 30

def check_flood(user_id):

    current_time = time.time()

    last_time = user_last_message.get(user_id)

    if last_time:

        if current_time - last_time < COOLDOWN:

            return False

    user_last_message[user_id] = current_time

    return True