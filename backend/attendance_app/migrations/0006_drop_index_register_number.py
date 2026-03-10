from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0005_drop_stuck_unique_constraint'),
    ]

    operations = [
        migrations.RunSQL("""
            DO $$ 
            DECLARE 
                idx_name TEXT;
            BEGIN
                -- Drop any unique index that is ONLY on register_number
                -- This targets indices that might not be registered as constraints
                FOR idx_name IN (
                    SELECT i.relname
                    FROM pg_index x
                    JOIN pg_class c ON c.oid = x.indrelid
                    JOIN pg_class i ON i.oid = x.indexrelid
                    JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = ANY(x.indkey)
                    WHERE c.relname = 'attendance_app_student'
                    AND x.indisunique = true
                    AND a.attname = 'register_number'
                    AND (SELECT count(*) FROM pg_attribute a2 WHERE a2.attrelid = c.oid AND a2.attnum = ANY(x.indkey)) = 1
                ) LOOP
                    EXECUTE 'DROP INDEX IF EXISTS ' || idx_name || ' CASCADE';
                END LOOP;
            END $$;
        """),
    ]
