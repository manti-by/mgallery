def test_thumbnails_path_set():
    from mgallery import settings
    assert settings.THUMBNAILS_PATH

def test_redis_url_set():
    from mgallery import settings
    assert settings.REDIS_URL

def test_file_types():
    from mgallery import settings
    expected = ("arw", "dng", "jpg", "jpeg", "png", "webp", "gif")
    assert settings.FILE_TYPES == expected

def test_num_processes():
    from mgallery import settings
    assert settings.NUM_PROCESSES >= 0

def test_logging_config():
    from mgallery import settings
    logging = settings.LOGGING
    assert logging["version"] == 1
    handlers = logging.get("handlers", {})
    assert isinstance(handlers, dict)
