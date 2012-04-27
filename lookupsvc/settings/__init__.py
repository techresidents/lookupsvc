import os

if "SERVICE_ENV" in os.environ:
    if os.environ["SERVICE_ENV"] == "localdev":
        from settings.localdev_settings import *
    elif os.environ["SERVICE_ENV"] == "integration":
        from settings.inteegration_settings import *
    elif os.environ["SERVICE_ENV"] == "staging":
        from settings.staging_settings import *
    elif os.environ["SERVICE_ENV"] == "prod":
        from settings.prod_settings import *
    else:
        from settings.default_settings import *
else:
    from settings.default_settings import *

__all__ = []
