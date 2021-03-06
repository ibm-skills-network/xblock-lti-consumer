# Generated by Django 2.2.16 on 2020-10-24 11:47

from django.db import migrations, models, transaction


def _load_block(location):
    """
    Loads block from modulestore.
    """
    from xmodule.modulestore.django import modulestore
    return modulestore().get_item(location)


def forwards_func(apps, schema_editor):
    """
    Forward migration - copy client ID and save it in Model
    """
    LtiConfiguration = apps.get_model("lti_consumer", "LtiConfiguration")
    db_alias = schema_editor.connection.alias

    lti_configs = LtiConfiguration.objects.select_for_update().filter(
        version="lti_1p3",
    )
    with transaction.atomic():
        for lti_config in lti_configs:
            if not lti_config.location:
                continue
            block = _load_block(lti_config.location)

            # If client_id exists, move it to model
            if hasattr(block, 'lti_1p3_client_id'):
                lti_config.lti_1p3_client_id = block.lti_1p3_client_id

                # If key exists, move it to model. Set kid as client_id, respecting
                # old implementation
                if hasattr(block, 'lti_1p3_block_key'):
                    lti_config.lti_1p3_internal_private_key_id = block.lti_1p3_client_id
                    lti_config.lti_1p3_internal_private_key = block.lti_1p3_block_key

            # Save if something changed
            lti_config.save()


def reverse_func(apps, schema_editor):
    """
    Reverse migration - No op.

    Leave XBlock to regenerate Client ID and secrets.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('lti_consumer', '0004_keyset_mgmt_to_model'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
            reverse_func
        ),
    ]
