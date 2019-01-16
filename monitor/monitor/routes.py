def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('dashboard', '/')
    config.add_route('receiver', '/receiver')
