from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [

        # ---------------------------------------------------------
        # BillItem ordering
        # ---------------------------------------------------------
        migrations.AlterModelOptions(
            name='billitem',
            options={'ordering': ['bill_item_id']},
        ),

        # ---------------------------------------------------------
        # Rename existing primary-key columns
        # This preserves the existing ID values.
        # ---------------------------------------------------------

        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE core_category
                        RENAME COLUMN id TO category_id;
                    """,
                    reverse_sql="""
                        ALTER TABLE core_category
                        RENAME COLUMN category_id TO id;
                    """,
                ),
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE core_supplier
                        RENAME COLUMN id TO supplier_id;
                    """,
                    reverse_sql="""
                        ALTER TABLE core_supplier
                        RENAME COLUMN supplier_id TO id;
                    """,
                ),
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE core_customer
                        RENAME COLUMN id TO customer_id;
                    """,
                    reverse_sql="""
                        ALTER TABLE core_customer
                        RENAME COLUMN customer_id TO id;
                    """,
                ),
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE core_medicine
                        RENAME COLUMN id TO medicine_id;
                    """,
                    reverse_sql="""
                        ALTER TABLE core_medicine
                        RENAME COLUMN medicine_id TO id;
                    """,
                ),
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE core_bill
                        RENAME COLUMN id TO bill_id;
                    """,
                    reverse_sql="""
                        ALTER TABLE core_bill
                        RENAME COLUMN bill_id TO id;
                    """,
                ),
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE core_billitem
                        RENAME COLUMN id TO bill_item_id;
                    """,
                    reverse_sql="""
                        ALTER TABLE core_billitem
                        RENAME COLUMN bill_item_id TO id;
                    """,
                ),
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE core_activitylog
                        RENAME COLUMN id TO activity_log_id;
                    """,
                    reverse_sql="""
                        ALTER TABLE core_activitylog
                        RENAME COLUMN activity_log_id TO id;
                    """,
                ),

                # Remove Supplier timestamps from the actual database.
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE core_supplier
                        DROP COLUMN created_at;
                    """,
                    reverse_sql="""
                        ALTER TABLE core_supplier
                        ADD COLUMN created_at DATETIME(6) NOT NULL;
                    """,
                ),
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE core_supplier
                        DROP COLUMN updated_at;
                    """,
                    reverse_sql="""
                        ALTER TABLE core_supplier
                        ADD COLUMN updated_at DATETIME(6) NOT NULL;
                    """,
                ),
            ],

            state_operations=[
                migrations.RemoveField(
                    model_name='category',
                    name='id',
                ),
                migrations.AddField(
                    model_name='category',
                    name='category_id',
                    field=models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                    ),
                ),

                migrations.RemoveField(
                    model_name='supplier',
                    name='id',
                ),
                migrations.RemoveField(
                    model_name='supplier',
                    name='created_at',
                ),
                migrations.RemoveField(
                    model_name='supplier',
                    name='updated_at',
                ),
                migrations.AddField(
                    model_name='supplier',
                    name='supplier_id',
                    field=models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                    ),
                ),

                migrations.RemoveField(
                    model_name='customer',
                    name='id',
                ),
                migrations.AddField(
                    model_name='customer',
                    name='customer_id',
                    field=models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                    ),
                ),

                migrations.RemoveField(
                    model_name='medicine',
                    name='id',
                ),
                migrations.AddField(
                    model_name='medicine',
                    name='medicine_id',
                    field=models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                    ),
                ),

                migrations.RemoveField(
                    model_name='bill',
                    name='id',
                ),
                migrations.AddField(
                    model_name='bill',
                    name='bill_id',
                    field=models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                    ),
                ),

                migrations.RemoveField(
                    model_name='billitem',
                    name='id',
                ),
                migrations.AddField(
                    model_name='billitem',
                    name='bill_item_id',
                    field=models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                    ),
                ),

                migrations.RemoveField(
                    model_name='activitylog',
                    name='id',
                ),
                migrations.AddField(
                    model_name='activitylog',
                    name='activity_log_id',
                    field=models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                    ),
                ),
            ],
        ),

        # ---------------------------------------------------------
        # Existing index names
        # ---------------------------------------------------------

        migrations.RenameIndex(
            model_name='medicine',
            new_name='core_medici_expiry__d093fc_idx',
            old_name='core_medici_expiry__b8e6a4_idx',
        ),

        migrations.RenameIndex(
            model_name='medicine',
            new_name='core_medici_code_a161e1_idx',
            old_name='core_medici_code_1c9d3e_idx',
        ),

        # ---------------------------------------------------------
        # Field-size changes
        # ---------------------------------------------------------

        migrations.AlterField(
            model_name='category',
            name='description',
            field=models.CharField(
                blank=True,
                max_length=100,
            ),
        ),

        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(
                max_length=30,
                unique=True,
            ),
        ),

        migrations.AlterField(
            model_name='customer',
            name='name',
            field=models.CharField(
                max_length=30,
            ),
        ),

        migrations.AlterField(
            model_name='customer',
            name='phone',
            field=models.CharField(
                max_length=12,
            ),
        ),

        migrations.AlterField(
            model_name='medicine',
            name='batch_number',
            field=models.CharField(
                max_length=10,
                verbose_name='Batch Number',
            ),
        ),

        migrations.AlterField(
            model_name='medicine',
            name='code',
            field=models.CharField(
                max_length=10,
                unique=True,
                verbose_name='Medicine Code',
            ),
        ),

        migrations.AlterField(
            model_name='medicine',
            name='name',
            field=models.CharField(
                max_length=50,
                verbose_name='Medicine Name',
            ),
        ),

        migrations.AlterField(
            model_name='supplier',
            name='contact_person',
            field=models.CharField(
                blank=True,
                max_length=30,
            ),
        ),

        migrations.AlterField(
            model_name='supplier',
            name='phone',
            field=models.CharField(
                max_length=12,
            ),
        ),
    ]