class Photobot_Camera(object):


    @classmethod
    def get_default_values(cls):
        defaults = dict()

        defaults['port'] = 80
        defaults['enable'] = 1
        defaults['delay_between_photos']=3
        defaults['photos_per_round']=3
        defaults['seconds_between_starts'] = 60
        defaults['run_at_night'] = 0
        #defaults['number_of_rounds'] = 1
        #defaults['delay_between_rounds'] = 5
        defaults['user'] = 'admin'
        defaults['wsdl_dir'] = '/var/photobot/env2/wsdl'
        return defaults

    @classmethod
    def customize_defaults(cls,defaults):
        return defaults

    @classmethod
    def get_default_value(cls,name):
        defaults = cls.get_default_values()
        defaults = cls.customize_defaults(defaults)

        default_val = defaults.get(name)
        if not default_val:
            return ""

        return default_val

    def setting(self,setting_name):

        default_value = self.get_default_value(setting_name)
        return str(self.settings.get(setting_name,default_value))
