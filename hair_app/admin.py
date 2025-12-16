# Создать кастомный админ сайт
custom_admin_site = CustomAdminSite(name='custom_admin')


@custom_admin_site.register(HairApplication)