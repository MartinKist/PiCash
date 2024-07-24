from configuration import Config
from register import Register


Config().load_config_file("./config.json")
r = Register()
r.run()
