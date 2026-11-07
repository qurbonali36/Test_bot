import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import certificate

try:
    # Use some dummy values for testing
    res = certificate.generate_certificate_files(
        chat_id=12345678, # this user needs to exist in the db if we want their name, else fallback to 'User'
        test_id="test_dummy_123",
        correct=10,
        total=10,
        user_point=100,
        percent=100.0,
        lang_id=1,
        bot_username="DummyBot"
    )
    print("Generated successfully:")
    print(res)
except Exception as e:
    import traceback
    traceback.print_exc()
