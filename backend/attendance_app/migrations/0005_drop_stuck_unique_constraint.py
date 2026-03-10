from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0004_rename_roll_id_student_register_number_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DO $$
            DECLARE
                r RECORD;
            BEGIN
                FOR r IN (
                    SELECT conname
                    FROM pg_constraint
                    WHERE conrelid = 'attendance_app_student'::regclass
                    AND contype = 'u'
                    AND EXISTS (
                        SELECT 1 FROM pg_attribute
                        WHERE attrelid = 'attendance_app_student'::regclass
                        AND attname = 'register_number'
                        AND attnum = ANY(conkey)
                    )
                ) LOOP
                    EXECUTE 'ALTER TABLE attendance_app_student DROP CONSTRAINT ' || quote_ident(r.conname);
                END LOOP;
            END $$;
            """
        ),
    ]
