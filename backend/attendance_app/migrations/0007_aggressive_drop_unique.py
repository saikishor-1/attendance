from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0006_drop_index_register_number'),
    ]

    operations = [
        # Ultra-simple, aggressive drop of the most likely constraint name
        migrations.RunSQL("ALTER TABLE attendance_app_student DROP CONSTRAINT IF EXISTS attendance_app_student_register_number_key CASCADE;"),
        migrations.RunSQL("DROP INDEX IF EXISTS attendance_app_student_register_number_key CASCADE;"),
        migrations.RunSQL("DROP INDEX IF EXISTS attendance_app_student_register_number_unique CASCADE;"),
    ]
