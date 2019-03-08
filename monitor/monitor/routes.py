from pyramid.response import Response
def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('samples', config.registry.settings['image_samples_dir'], cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('dashboard', '/dashboard')
    config.add_route('receiver', '/ping')
    config.add_route('notifications', '/notifications')
    config.add_route('installations', '/installations')
    config.add_route('pings', '/pings')
    config.add_route('pings_by_install', '/log/{install}')
    config.add_route('pings_by_subsystem', '/log/{install}/{subsystem}')
    config.add_route('image_samples', '/samples')
    config.add_route('image_samples_by_install', '/samps/{install_id}')
