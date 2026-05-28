import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from core.middleware import set_current_tenant_id
from core.models import Tenant, User
from ingestion.models import IngestionBatch
from ingestion.services import ingest_file


class Command(BaseCommand):
    help = "Seed Acme tenant, users, sample CSV files, and ingested ESG data."

    def handle(self, *args, **options):
        tenant, _ = Tenant.objects.get_or_create(name="Acme Corp", slug="acme-corp")
        admin = self.upsert_user("admin@acme.com", "admin", "acmeadmin123", tenant)
        self.upsert_user("analyst@acme.com", "analyst", "acmeanalyst123", tenant)
        set_current_tenant_id(tenant.id)

        sample_dir = Path.cwd() / "sample_data"
        sample_dir.mkdir(exist_ok=True)

        files = {
            IngestionBatch.SOURCE_SAP: self.write_csv(sample_dir / "sap_sample.csv", self.sap_rows()),
            IngestionBatch.SOURCE_UTILITY: self.write_csv(sample_dir / "utility_sample.csv", self.utility_rows()),
            IngestionBatch.SOURCE_TRAVEL: self.write_csv(sample_dir / "travel_sample.csv", self.travel_rows()),
        }

        for source_type, path in files.items():
            IngestionBatch.all_objects.filter(tenant=tenant, filename=path.name).delete()
            with path.open("rb") as file_obj:
                batch = ingest_file(
                    tenant=tenant,
                    user=admin,
                    file_obj=file_obj,
                    source_type=source_type,
                    filename=path.name,
                    allow_duplicate=True,
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Ingested {path.name}: batch={batch.id}, rows={batch.row_count}, errors={batch.error_count}"
                )
            )

    def upsert_user(self, email, role, password, tenant):
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": email.split("@")[0], "role": role, "tenant": tenant},
        )
        user.tenant = tenant
        user.role = role
        user.set_password(password)
        user.save()
        return user

    def write_csv(self, path, rows):
        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return path

    def sap_rows(self):
        return [
            {"Posting Date": "01.01.2024", "Plant": "IN01", "Material": "DIESEL-HSD", "Movement Type": "261", "Quantity": "1250.50", "Base Unit of Measure": "L", "Cost Center": "CC100", "Vendor": "FuelCo"},
            {"Posting Date": "02.01.2024", "Plant": "IN02", "Material": "PETROL-MS", "Movement Type": "261", "Quantity": "840", "Base Unit of Measure": "L", "Cost Center": "CC200", "Vendor": "FuelCo"},
            {"Posting Date": "03.01.2024", "Plant": "IN01", "Material": "LPG-BULK", "Movement Type": "261", "Quantity": "520", "Base Unit of Measure": "KG", "Cost Center": "CC100", "Vendor": "GasOne"},
            {"Posting Date": "01/04/2024", "Plant": "IN02", "Material": "DIESEL-HSD", "Movement Type": "261", "Quantity": "1000,75", "Base Unit of Measure": "L", "Cost Center": "CC200", "Vendor": "FuelCo"},
            {"Posting Date": "2024-01-05", "Plant": "IN01", "Material": "PETROL-MS", "Movement Type": "201", "Quantity": "650", "Base Unit of Measure": "L", "Cost Center": "CC300", "Vendor": "FuelCo"},
            {"Posting Date": "06.01.2024", "Plant": "IN02", "Material": "LPG-BULK", "Movement Type": "551", "Quantity": "430", "Base Unit of Measure": "KG", "Cost Center": "CC200", "Vendor": "GasOne"},
            {"Posting Date": "07.01.2024", "Plant": "IN01", "Material": "DIESEL-HSD", "Movement Type": "261", "Quantity": "300", "Base Unit of Measure": "MT", "Cost Center": "CC100", "Vendor": "FuelCo"},
            {"Posting Date": "08.01.2024", "Plant": "IN02", "Material": "PETROL-MS", "Movement Type": "101", "Quantity": "900", "Base Unit of Measure": "L", "Cost Center": "CC200", "Vendor": "FuelCo"},
            {"Posting Date": "09.01.2024", "Plant": "IN01", "Material": "DIESEL-HSD", "Movement Type": "261", "Quantity": "1125", "Base Unit of Measure": "L", "Cost Center": "CC100", "Vendor": "FuelCo"},
            {"Posting Date": "10.01.2024", "Plant": "IN02", "Material": "LPG-BULK", "Movement Type": "261", "Quantity": "610", "Base Unit of Measure": "KG", "Cost Center": "CC200", "Vendor": "GasOne"},
        ]

    def utility_rows(self):
        return [
            {"Consumer Number": "MTR-100", "Billing Period From": "2024-01-03", "Billing Period To": "2024-02-02", "Units Consumed": "12340", "Unit": "kWh", "Site Name": "Mumbai Plant", "Tariff Category": "HT-I"},
            {"Consumer Number": "MTR-101", "Billing Period From": "2024-01-10", "Billing Period To": "2024-02-09", "Units Consumed": "9800", "Unit": "kWh", "Site Name": "Mumbai Plant", "Tariff Category": "HT-I"},
            {"Consumer Number": "MTR-200", "Billing Period From": "2024-01-15", "Billing Period To": "2024-02-14", "Units Consumed": "14.2", "Unit": "MWh", "Site Name": "Bangalore Plant", "Tariff Category": "HT-II"},
            {"Consumer Number": "MTR-100", "Billing Period From": "2024-02-03", "Billing Period To": "2024-03-02", "Units Consumed": "11950", "Unit": "kWh", "Site Name": "Mumbai Plant", "Tariff Category": "HT-I"},
            {"Consumer Number": "MTR-101", "Billing Period From": "2024-02-10", "Billing Period To": "2024-03-09", "Units Consumed": "10125", "Unit": "kWh", "Site Name": "Mumbai Plant", "Tariff Category": "HT-I"},
            {"Consumer Number": "MTR-200", "Billing Period From": "2024-02-15", "Billing Period To": "2024-03-14", "Units Consumed": "15100", "Unit": "kWh", "Site Name": "Bangalore Plant", "Tariff Category": "HT-II"},
            {"Consumer Number": "MTR-100", "Billing Period From": "2024-03-03", "Billing Period To": "2024-04-02", "Units Consumed": "", "Unit": "kWh", "Site Name": "Mumbai Plant", "Tariff Category": "HT-I"},
            {"Consumer Number": "MTR-200", "Billing Period From": "2024-03-15", "Billing Period To": "2024-04-14", "Units Consumed": "14775", "Unit": "kWh", "Site Name": "Bangalore Plant", "Tariff Category": "HT-II"},
        ]

    def travel_rows(self):
        return [
            {"Employee ID": "E001", "Transaction Date": "2024-01-05", "Expense Type": "Airfare", "Origin Airport Code": "BOM", "Destination Airport Code": "DEL", "Travel Class": "economy", "Distance": "", "Distance Unit": "", "Amount": "12000", "Currency Code": "INR", "Vendor Name": "Indigo"},
            {"Employee ID": "E002", "Transaction Date": "2024-01-06", "Expense Type": "Flight", "Origin Airport Code": "DEL", "Destination Airport Code": "LHR", "Travel Class": "business", "Distance": "", "Distance Unit": "", "Amount": "240000", "Currency Code": "INR", "Vendor Name": "British Airways"},
            {"Employee ID": "E003", "Transaction Date": "2024-01-07", "Expense Type": "Air", "Origin Airport Code": "BOM", "Destination Airport Code": "SIN", "Travel Class": "economy", "Distance": "2440", "Distance Unit": "km", "Amount": "36000", "Currency Code": "INR", "Vendor Name": "Singapore Airlines"},
            {"Employee ID": "E004", "Transaction Date": "2024-01-08", "Expense Type": "Airfare", "Origin Airport Code": "HYD", "Destination Airport Code": "BOM", "Travel Class": "economy", "Distance": "", "Distance Unit": "", "Amount": "9000", "Currency Code": "INR", "Vendor Name": "Vistara"},
            {"Employee ID": "E005", "Transaction Date": "2024-01-09", "Expense Type": "Flight", "Origin Airport Code": "DEL", "Destination Airport Code": "DXB", "Travel Class": "business", "Distance": "1360", "Distance Unit": "miles", "Amount": "82000", "Currency Code": "INR", "Vendor Name": "Emirates"},
            {"Employee ID": "E006", "Transaction Date": "2024-01-10", "Expense Type": "Airfare", "Origin Airport Code": "BOM", "Destination Airport Code": "DEL", "Travel Class": "business", "Distance": "", "Distance Unit": "", "Amount": "32000", "Currency Code": "INR", "Vendor Name": "Air India"},
            {"Employee ID": "E007", "Transaction Date": "2024-01-11", "Expense Type": "Air", "Origin Airport Code": "DEL", "Destination Airport Code": "LHR", "Travel Class": "economy", "Distance": "", "Distance Unit": "", "Amount": "78000", "Currency Code": "INR", "Vendor Name": "Virgin Atlantic"},
            {"Employee ID": "E008", "Transaction Date": "2024-01-12", "Expense Type": "Airfare", "Origin Airport Code": "XXX", "Destination Airport Code": "BOM", "Travel Class": "economy", "Distance": "", "Distance Unit": "", "Amount": "11000", "Currency Code": "INR", "Vendor Name": "Unknown Air"},
            {"Employee ID": "E009", "Transaction Date": "2024-01-13", "Expense Type": "Hotel", "Origin Airport Code": "BOM", "Destination Airport Code": "DEL", "Travel Class": "economy", "Distance": "", "Distance Unit": "", "Amount": "15000", "Currency Code": "INR", "Vendor Name": "Hotel One"},
            {"Employee ID": "E010", "Transaction Date": "2024-01-14", "Expense Type": "Hotel", "Origin Airport Code": "DEL", "Destination Airport Code": "DXB", "Travel Class": "economy", "Distance": "", "Distance Unit": "", "Amount": "18000", "Currency Code": "INR", "Vendor Name": "Hotel Two"},
            {"Employee ID": "E011", "Transaction Date": "2024-01-15", "Expense Type": "Flight", "Origin Airport Code": "BOM", "Destination Airport Code": "SIN", "Travel Class": "business", "Distance": "", "Distance Unit": "", "Amount": "125000", "Currency Code": "INR", "Vendor Name": "Singapore Airlines"},
            {"Employee ID": "E012", "Transaction Date": "2024-01-16", "Expense Type": "Airfare", "Origin Airport Code": "HYD", "Destination Airport Code": "BOM", "Travel Class": "economy", "Distance": "390", "Distance Unit": "miles", "Amount": "9500", "Currency Code": "INR", "Vendor Name": "Indigo"},
        ]
