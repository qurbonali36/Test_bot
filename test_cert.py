import traceback
try:
    from certificate import send_certificate
    class DummyBot:
        username = 'testbot'
        def send_photo(self, **kwargs):
            print('send_photo OK')
        def send_document(self, **kwargs):
            print('send_document OK')
    class DummyContext:
        bot = DummyBot()
    print('Testing...')
    send_certificate(DummyContext(), 7926940039, 'test_123', 14, 14, 14, 100.0, 1)
except Exception:
    traceback.print_exc()