# Configuration for Jupyter Lab
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.allow_root = True
c.ServerApp.token = 'eda_token_123'
c.ServerApp.password = ''
c.ServerApp.notebook_dir = '/app/notebooks'

# Security settings
c.ServerApp.allow_remote_access = True
c.ServerApp.disable_check_xsrf = True

# Extensions
c.LabApp.default_url = '/lab'