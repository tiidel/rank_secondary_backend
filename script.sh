

from tenant.models import *

# CREATE TENANT
tenant = Client(schema_name="public", name="default server");
tenant.save();

# REGISTER DOMAIN 
domain = Domain(domain = "rank.azurewebsites.net/", tenant = tenant);
domain.save();