import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'tu@email.com', 'tupassword')
    print("Superusuario creado")
else:
    print("Ya existe")
```

Luego en el Pre-deploy Command pon:
```
python create_super.py
