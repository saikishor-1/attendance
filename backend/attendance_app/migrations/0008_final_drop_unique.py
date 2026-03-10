from django.db import migrations


class Migration(migrations.Migration):
    """
    Ultra-aggressive migration to drop any single-column unique index or constraint
    on the register_number field in the attendance_app_student table.
    This runs multiple approaches to ensure the constraint is dropped.
    """

    dependencies = [
        ('attendance_app', '0007_aggressive_drop_unique'),
    ]

    operations = [
        # Drop by typical auto-generated constraint names
        migrations.RunSQL(
            "ALTER TABLE attendance_app_student DROP CONSTRAINT IF EXISTS attendance_app_student_register_number_key;",
            reverse_sql="SELECT 1;"
        ),
        migrations.RunSQL(
            "ALTER TABLE attendance_app_student DROP CONSTRAINT IF EXISTS attendance_app_student_register_number_key CASCADE;",
            reverse_sql="SELECT 1;"
        ),
        # Drop any unique index that is only on register_number
        migrations.RunSQL("""
            DO $$
            DECLARE
                r RECORD;
            BEGIN
                FOR r IN (
                    SELECT i.relname AS index_name
                    FROM pg_index x
                    JOIN pg_class c ON c.oid = x.indrelid
                    JOIN pg_class i ON i.oid = x.indexrelid
                    WHERE c.relname = 'attendance_app_student'
                    AND x.indisunique = true
                    AND (
                        SELECT string_agg(a.attname, ',')
                        FROM pg_attribute a
                        WHERE a.attrelid = c.oid AND a.attnum = ANY(x.indkey) AND a.attnum > 0
                    ) = 'register_number'
                )
                LOOP
                    EXECUTE 'DROP INDEX IF EXISTS "' || r.index_name || '" CASCADE';
                END LOOP;
            END $$;
        """, reverse_sql="SELECT 1;"),
    ]
