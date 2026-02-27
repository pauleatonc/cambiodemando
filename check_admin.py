#!/usr/bin/env python
"""
Verificar superusuarios en la BD.
Uso dentro del contenedor: python manage.py shell < check_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cambiodemando.settings.dev')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
superusers = User.objects.filter(is_superuser=True)

if not superusers.exists():
    print("No hay superusuarios en la base de datos.")
    print("Crea uno con: python manage.py createsuperuser")
else:
    print("Superusuarios encontrados:")
    for u in superusers:
        print(f"  - {u.username} (email={u.email}, is_staff={u.is_staff})")
    print("\nPara restablecer la contraseña de 'admin':")
    print("  python manage.py changepassword admin")
