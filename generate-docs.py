from app.main import app

import yaml

with open("openapi.yaml", "w") as f:
    api_spec = app.openapi()
    yaml.dump(api_spec, f, allow_unicode=True)