jmbo-registration
=================

Migrating `registration` to `jmbo_registration`
***********************************************

`registration` was renamed to `jmbo_registration` to avoid clashing with `django-registration`. If migrations `0001` and `0002` had been run before
the renaming, you need to do the following:

1. Before running migrations, do ``UPDATE south_migrationhistory SET app_name = 'jmbo_registration' WHERE app_name = 'registration'``.
2. Run migrations - it will rename `registration` tables and content types to `jmbo_registration`.
