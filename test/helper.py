import nose.tools as nt


def assert_not_raises(proc, msg):
    try:
        proc.call()
    except:
        assert_true(False, msg)
