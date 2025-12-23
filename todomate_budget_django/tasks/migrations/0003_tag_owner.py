from django.db import migrations, models
from django.conf import settings


def assign_tag_owners(apps, schema_editor):
    Tag = apps.get_model("tasks", "Tag")
    Task = apps.get_model("tasks", "Task")
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))

    default_user = User.objects.order_by("id").first()
    for tag in Tag.objects.all():
        related_task = (
            Task.objects.filter(tags__id=tag.id)
            .select_related("owner")
            .order_by("id")
            .first()
        )
        owner = getattr(related_task, "owner", None) or default_user
        if owner:
            tag.owner = owner
            tag.save(update_fields=["owner"])
        else:
            # Tag without any owner or related task is removed to keep data consistent.
            tag.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0002_task_todo_date"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="tag",
            name="owner",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                on_delete=models.deletion.CASCADE,
                related_name="tags",
                null=True,
                blank=True,
            ),
        ),
        migrations.RunPython(assign_tag_owners, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="tag",
            name="owner",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                on_delete=models.deletion.CASCADE,
                related_name="tags",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="tag",
            unique_together={("owner", "name")},
        ),
    ]

