import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0006_rename_client_password_hash_client_client_password"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReturnRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("chat_id", models.CharField(blank=True, max_length=100, null=True)),
                ("request_date", models.DateTimeField(auto_now_add=True)),
                ("current_status", models.CharField(choices=[("Solicitado", "Solicitado"), ("Aceito", "Aceito"), ("Coletado", "Coletado"), ("Em trânsito", "Em trânsito"), ("Recebido pela empresa", "Recebido pela empresa"), ("Avaliado", "Avaliado"), ("Concluído", "Concluído"), ("Cancelado", "Cancelado")], default="Solicitado", max_length=25)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("client", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="return_requests", to="api.client")),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="return_requests", to="api.company")),
                ("device", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="return_request", to="api.device")),
                ("driver", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="return_requests", to="api.driver")),
            ],
        ),
        migrations.CreateModel(
            name="Ride",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("chat_id", models.CharField(blank=True, max_length=100, null=True)),
                ("current_status", models.CharField(choices=[("AGUARDANDO_MOTORISTA", "Aguardando motorista"), ("MOTORISTA_ACEITOU", "Motorista aceitou"), ("PRODUTO_RECOLHIDO", "Produto recolhido"), ("EM_TRANSITO", "Em trânsito"), ("ENTREGUE", "Entregue"), ("CANCELADA", "Cancelada")], default="AGUARDANDO_MOTORISTA", max_length=25)),
                ("requested_at", models.DateTimeField(auto_now_add=True)),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                ("collected_at", models.DateTimeField(blank=True, null=True)),
                ("delivered_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("client", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="rides", to="api.client")),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="rides", to="api.company")),
                ("device", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="ride", to="api.device")),
                ("driver", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="rides", to="api.driver")),
            ],
            options={"db_table": "ride"},
        ),
        migrations.CreateModel(
            name="RequestStatusHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("Solicitado", "Solicitado"), ("Aceito", "Aceito"), ("Coletado", "Coletado"), ("Em trânsito", "Em trânsito"), ("Recebido pela empresa", "Recebido pela empresa"), ("Avaliado", "Avaliado"), ("Concluído", "Concluído"), ("Cancelado", "Cancelado")], max_length=25)),
                ("changed_at", models.DateTimeField(auto_now_add=True)),
                ("return_request", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="status_history", to="api.returnrequest")),
            ],
            options={"ordering": ["changed_at"]},
        ),
        migrations.CreateModel(
            name="RideStatusHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("AGUARDANDO_MOTORISTA", "Aguardando motorista"), ("MOTORISTA_ACEITOU", "Motorista aceitou"), ("PRODUTO_RECOLHIDO", "Produto recolhido"), ("EM_TRANSITO", "Em trânsito"), ("ENTREGUE", "Entregue"), ("CANCELADA", "Cancelada")], max_length=25)),
                ("changed_at", models.DateTimeField(auto_now_add=True)),
                ("notes", models.CharField(blank=True, max_length=255, null=True)),
                ("ride", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="status_history", to="api.ride")),
            ],
            options={"db_table": "ride_status_history", "ordering": ["changed_at"]},
        ),
    ]
