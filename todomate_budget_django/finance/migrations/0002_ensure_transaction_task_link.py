from django.db import migrations


def ensure_task_link(apps, schema_editor):
    """Ensure the legacy databases also have the task_id column."""
    Transaction = apps.get_model('finance', 'Transaction')
    table_name = Transaction._meta.db_table
    connection = schema_editor.connection

    with connection.cursor() as cursor:
        existing_columns = {
            column.name for column in connection.introspection.get_table_description(cursor, table_name)
        }

    if 'task_id' not in existing_columns:
        # 이전 버전의 DB에서는 task_id가 빠져 있어 수동으로 필드를 추가해준다.
        schema_editor.add_field(Transaction, Transaction._meta.get_field('task'))


def reverse_code(apps, schema_editor):
    """Reverse function intentionally left empty because dropping the column would lose data."""
    # 되돌릴 때는 아무 작업도 하지 않는다. 이미 존재하는 컬럼을 삭제하면 데이터가 유실된다.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(ensure_task_link, reverse_code),
    ]
