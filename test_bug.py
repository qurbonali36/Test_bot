import logging
import traceback

class MockJob:
    def __init__(self, context):
        self.context = context

class MockBot:
    def __init__(self):
        self.username = "mock_bot"
    def send_message(self, *args, **kwargs):
        print("MockBot.send_message called with:", kwargs)

class MockJobQueue:
    def run_once(self, *args, **kwargs):
        print("MockJobQueue.run_once called with:", kwargs)

class MockContext:
    def __init__(self, job_context):
        self.job = MockJob(job_context)
        self.bot = MockBot()
        self.bot_data = {}
        self.job_queue = MockJobQueue()

def run_test():
    try:
        from quest_poll import send_polls
        xalta = {
            "chat_id": 12345,
            "test_id": "matematika_5",
            "current_quest": 5,
            "amount_quest": 5,
            "correct_ans": 4,
            "speed_bonus": 2,
            "name_link": "Foydalanuvchi"
        }
        ctx = MockContext({"xalta": xalta, "chat_id": 12345, "point": 1})
        send_polls(ctx)
        print("send_polls completed successfully!")
    except Exception as e:
        print("ERROR IN send_polls:")
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
