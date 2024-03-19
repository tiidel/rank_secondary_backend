

from tenant.models import *

# CREATE TENANT
tenant = Client(schema_name="public", name="default server");
tenant.save();

# REGISTER DOMAIN 
domain = Domain(domain = "localhost", tenant = tenant);
domain.save();