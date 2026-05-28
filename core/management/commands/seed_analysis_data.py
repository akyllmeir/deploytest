from django.core.management.base import BaseCommand
from core.models import AnalysisType, AnalysisParameter


class Command(BaseCommand):
    help = "Seed analysis types (KZ + RU)"

    def handle(self, *args, **kwargs):
        data = [
            {
                "code": "cbc",
                "name_kz": "Жалпы қан анализі",
                "name_ru": "Общий анализ крови",
                "description": "Complete blood count",
                "parameters": [
                    {"code": "hemoglobin", "name_kz": "Гемоглобин", "name_ru": "Гемоглобин", "unit": "g/dL", "value_type": "numeric"},
                    {"code": "wbc", "name_kz": "Лейкоциттер", "name_ru": "Лейкоциты", "unit": "x10^9/L", "value_type": "numeric"},
                    {"code": "platelets", "name_kz": "Тромбоциттер", "name_ru": "Тромбоциты", "unit": "x10^9/L", "value_type": "numeric"},
                    {"code": "rbc", "name_kz": "Эритроциттер", "name_ru": "Эритроциты", "unit": "x10^12/L", "value_type": "numeric"},
                    {"code": "esr", "name_kz": "СОЭ", "name_ru": "СОЭ", "unit": "mm/hr", "value_type": "numeric"},
                ],
            },
            {
                "code": "biochem",
                "name_kz": "Биохимиялық қан анализі",
                "name_ru": "Биохимический анализ крови",
                "description": "Biochemical blood test",
                "parameters": [
                    {"code": "glucose", "name_kz": "Глюкоза", "name_ru": "Глюкоза", "unit": "mmol/L", "value_type": "numeric"},
                    {"code": "alt", "name_kz": "АЛТ", "name_ru": "АЛТ", "unit": "U/L", "value_type": "numeric"},
                    {"code": "ast", "name_kz": "АСТ", "name_ru": "АСТ", "unit": "U/L", "value_type": "numeric"},
                    {"code": "bilirubin", "name_kz": "Билирубин", "name_ru": "Билирубин", "unit": "µmol/L", "value_type": "numeric"},
                    {"code": "creatinine", "name_kz": "Креатинин", "name_ru": "Креатинин", "unit": "µmol/L", "value_type": "numeric"},
                ],
            },
            {
                "code": "urine",
                "name_kz": "Жалпы зәр анализі",
                "name_ru": "Общий анализ мочи",
                "description": "General urinalysis",
                "parameters": [
                    {"code": "color", "name_kz": "Түсі", "name_ru": "Цвет", "unit": "", "value_type": "text"},
                    {"code": "ph", "name_kz": "pH", "name_ru": "pH", "unit": "", "value_type": "numeric"},
                    {"code": "protein", "name_kz": "Белок", "name_ru": "Белок", "unit": "", "value_type": "boolean"},
                    {"code": "glucose_urine", "name_kz": "Глюкоза", "name_ru": "Глюкоза", "unit": "", "value_type": "boolean"},
                    {"code": "ketones", "name_kz": "Кетондар", "name_ru": "Кетоны", "unit": "", "value_type": "boolean"},
                ],
            },
        ]

        created_types = 0
        created_params = 0

        for analysis in data:
            analysis_type, created = AnalysisType.objects.get_or_create(
                code=analysis["code"],
                defaults={
                    "name_kz": analysis["name_kz"],
                    "name_ru": analysis["name_ru"],
                    "description": analysis["description"],
                }
            )

            if not created:
                analysis_type.name_kz = analysis["name_kz"]
                analysis_type.name_ru = analysis["name_ru"]
                analysis_type.description = analysis["description"]
                analysis_type.save(update_fields=["name_kz", "name_ru", "description"])
            else:
                created_types += 1

            for param in analysis["parameters"]:
                _, param_created = AnalysisParameter.objects.update_or_create(
                    analysis_type=analysis_type,
                    code=param["code"],
                    defaults={
                        "name_kz": param["name_kz"],
                        "name_ru": param["name_ru"],
                        "unit": param.get("unit", ""),
                        "value_type": param.get("value_type", "numeric"),
                    }
                )

                if param_created:
                    created_params += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created analysis types: {created_types}, created parameters: {created_params}"
            )
        )