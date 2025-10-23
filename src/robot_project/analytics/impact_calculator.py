from typing import Dict, Tuple

class ImpactCalculator:
    """Calculadora de impacto ambiental con equivalencias locales"""

    def __init__(self, location: str = "Lima"):
        self.location = location
        self.equivalences = self._load_equivalences()
        self.local_references = self._load_local_references()

    def _load_equivalences(self) -> Dict:
        """Carga las equivalencias de impacto por tipo de residuo"""
        return {
            "plastico": {
                "energia_min": 15,  # minutos de iluminación
                "agua_litros": 2,
                "co2_gramos": 50,
                "descripcion": "Se convertirá en fibra para ropa nueva"
            },
            "papel": {
                "energia_min": 10,
                "agua_litros": 50,
                "arboles_por_ton": 17,
                "co2_gramos": 30,
                "descripcion": "Se reciclará en nuevo papel"
            },
            "carton": {
                "energia_min": 12,
                "agua_litros": 50,
                "arboles_por_ton": 17,
                "co2_gramos": 35,
                "descripcion": "Se convertirá en nuevas cajas"
            },
            "residuo_general": {
                "energia_min": 0,
                "agua_litros": 0,
                "co2_gramos": 0,
                "descripcion": "Disposición final controlada"
            }
        }

    def _load_local_references(self) -> Dict:
        """Carga referencias locales según ubicación"""
        references = {
            "Lima": {
                "parque": "Parque Kennedy",
                "landmark": "Costa Verde",
                "estadio": "Estadio Nacional"
            },
            "Bogotá": {
                "parque": "Parque Simón Bolívar",
                "landmark": "Cerro de Monserrate",
                "estadio": "Estadio El Campín"
            },
            "Default": {
                "parque": "parque local",
                "landmark": "zona verde",
                "estadio": "estadio municipal"
            }
        }
        return references.get(self.location, references["Default"])

    def calculate_single_item_impact(self, waste_type: str) -> Dict[str, str]:
        """
        Calcula el impacto de un solo item reciclado.

        Args:
            waste_type: Tipo de residuo (plastico, papel, carton, residuo_general)

        Returns:
            Dict con información de impacto
        """
        equiv = self.equivalences.get(waste_type, self.equivalences["residuo_general"])

        if waste_type == "residuo_general":
            return {
                "energia": "N/A",
                "agua": "N/A",
                "local_impact": "Gracias por usar el contenedor correcto",
                "descripcion": equiv["descripcion"]
            }

        energia_min = equiv["energia_min"]
        local_ref = self.local_references["parque"]

        return {
            "energia": f"{energia_min} min de iluminación",
            "agua": f"{equiv['agua_litros']} litros ahorrados",
            "co2": f"{equiv['co2_gramos']}g CO2 evitados",
            "local_impact": f"Energía para iluminar {local_ref} durante {energia_min} minutos",
            "descripcion": equiv["descripcion"]
        }

    def calculate_accumulated_impact(self, recycling_history: Dict[str, int]) -> Dict:
        """
        Calcula el impacto acumulado de un usuario.

        Args:
            recycling_history: Dict con conteo por tipo {"plastico": 10, "papel": 5, ...}

        Returns:
            Dict con impacto total acumulado
        """
        total_energia_min = 0
        total_agua_litros = 0
        total_co2_gramos = 0
        total_items = 0

        for waste_type, count in recycling_history.items():
            if waste_type in self.equivalences:
                equiv = self.equivalences[waste_type]
                total_energia_min += equiv["energia_min"] * count
                total_agua_litros += equiv["agua_litros"] * count
                total_co2_gramos += equiv["co2_gramos"] * count
                total_items += count

        # Convertir a formatos legibles
        energia_horas = total_energia_min / 60
        arboles_equivalentes = total_items / 100  # Aproximación: 100 items = 1 árbol/año

        return {
            "total_items": total_items,
            "energia_horas": round(energia_horas, 2),
            "agua_litros": total_agua_litros,
            "co2_kg": round(total_co2_gramos / 1000, 2),
            "arboles_equivalentes": round(arboles_equivalentes, 1)
        }

    def get_local_impact_message(self, waste_type: str, count: int = 1) -> str:
        """
        Genera mensaje de impacto local personalizado.

        Args:
            waste_type: Tipo de residuo
            count: Cantidad de items

        Returns:
            Mensaje personalizado con referencia local
        """
        impact = self.calculate_single_item_impact(waste_type)

        if waste_type == "residuo_general":
            return impact["local_impact"]

        local_ref = self.local_references["parque"]
        equiv = self.equivalences[waste_type]
        total_min = equiv["energia_min"] * count

        if count == 1:
            return f"1 {waste_type} = ⚡ {total_min} min de luz en {local_ref}"
        else:
            horas = total_min / 60
            return f"{count} {waste_type}s = ⚡ {horas:.1f} horas de luz en {local_ref}"

    def get_ranking_message(self, percentile: float, district: str = "") -> str:
        """
        Genera mensaje de ranking del usuario.

        Args:
            percentile: Percentil del usuario (0-100)
            district: Nombre del distrito/zona

        Returns:
            Mensaje de ranking
        """
        district_text = f"en {district}" if district else ""

        if percentile >= 95:
            return f"Top {100-percentile:.0f}% {district_text} 🏆⭐⭐⭐"
        elif percentile >= 80:
            return f"Top {100-percentile:.0f}% {district_text} 🏆⭐⭐"
        elif percentile >= 50:
            return f"Top {100-percentile:.0f}% {district_text} 🏆⭐"
        else:
            return f"Posición: {percentile:.0f}% {district_text} 💪"

    def format_impact_for_display(self, accumulated_impact: Dict) -> Dict[str, str]:
        """
        Formatea el impacto acumulado para mostrar en pantalla.

        Args:
            accumulated_impact: Dict de calculate_accumulated_impact()

        Returns:
            Dict con strings formateados para display
        """
        return {
            "energia": f"⚡ {accumulated_impact['energia_horas']} horas de energía",
            "agua": f"💧 {accumulated_impact['agua_litros']} litros de agua ahorrados",
            "co2": f"🌱 {accumulated_impact['co2_kg']} kg CO2 evitados",
            "arboles": f"🌳 Equivale a plantar {accumulated_impact['arboles_equivalentes']} árboles al año"
        }
